from __future__ import annotations

import argparse
import logging
from pathlib import Path

from chunker.config import ChunkerConfig
from chunker.loaders import load_document
from chunker.pipeline import Pipeline

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chunker",
        description="Hierarchical document chunking with multi-level summaries",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Process a document")
    run_parser.add_argument(
        "input_file", help="Path to input file (text, markdown, or .pdf)"
    )
    run_parser.add_argument("--model", default=None, help="Model name")
    run_parser.add_argument("--output-dir", default=None, help="Output directory")
    run_parser.add_argument(
        "--rewrite-instructions",
        default=None,
        help="Instructions for how the LLM should rewrite text "
        "(e.g., 'rewrite so a non-ML specialist can understand it')",
    )
    run_parser.add_argument(
        "--pdf-dpi",
        type=int,
        default=None,
        help="Resolution (DPI) for rendering PDF pages to images (PDF input only)",
    )
    run_parser.add_argument(
        "--vision-model",
        default=None,
        help="Vision-capable model used to rewrite PDF chunks "
        "(PDF input only; defaults to --model)",
    )

    resume_parser = subparsers.add_parser("resume", help="Resume from checkpoint")
    resume_parser.add_argument("checkpoint_file", help="Path to checkpoint file")
    resume_parser.add_argument("--output-dir", default=None, help="Output directory")
    resume_parser.add_argument("--model", default=None, help="Model name")
    resume_parser.add_argument(
        "--vision-model",
        default=None,
        help="Vision-capable model for resuming a PDF run "
        "(a PDF resume needs a vision model for rewrite)",
    )

    return parser


def run_command(args: argparse.Namespace) -> None:
    input_path = Path(args.input_file)

    config_kwargs = {}
    if args.rewrite_instructions:
        config_kwargs["rewrite_instructions"] = args.rewrite_instructions
    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir
        config_kwargs["checkpoint_path"] = str(
            Path(args.output_dir) / "checkpoint.json"
        )
    if args.pdf_dpi is not None:
        config_kwargs["pdf_dpi"] = args.pdf_dpi
    if args.vision_model:
        config_kwargs["vision_model"] = args.vision_model

    if args.model:
        config = ChunkerConfig.from_model(args.model, **config_kwargs)
    else:
        config = ChunkerConfig(**config_kwargs)

    # `.pdf` → pdf mode (rendered pages); any other suffix → text mode. No
    # separate text-extraction step runs for a PDF (FR-01).
    document = load_document(str(input_path), config)

    # A PDF is rewritten with vision, so the single injected model must be
    # multimodal: promote the chosen vision model to the effective model
    # before the Pipeline builds its ChatOllama (FR-11).
    if document.pages is not None and config.vision_model:
        config.model = config.vision_model

    pipeline = Pipeline(config)
    result = pipeline.run_document(document)

    logger.info(
        "Done: %d chunks, %d blocks, %d roots",
        result.total_chunks,
        result.total_blocks,
        len(result.root_block_ids),
    )


def resume_command(args: argparse.Namespace) -> None:
    config_kwargs = {"checkpoint_path": args.checkpoint_file}
    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir
    if args.vision_model:
        config_kwargs["vision_model"] = args.vision_model

    if args.model:
        config = ChunkerConfig.from_model(args.model, **config_kwargs)
    else:
        config = ChunkerConfig(**config_kwargs)

    # Mode is recovered from the checkpoint, so we cannot sniff it here. When a
    # vision model is supplied (a PDF resume), promote it to the effective model
    # the Pipeline builds its ChatOllama from.
    if config.vision_model:
        config.model = config.vision_model

    pipeline = Pipeline(config)
    result = pipeline.resume()

    logger.info(
        "Resumed: %d chunks, %d blocks, %d roots",
        result.total_chunks,
        result.total_blocks,
        len(result.root_block_ids),
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        run_command(args)
    elif args.command == "resume":
        resume_command(args)


if __name__ == "__main__":
    main()
