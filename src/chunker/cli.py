from __future__ import annotations

import argparse
import logging
from pathlib import Path

from chunker.config import ChunkerConfig
from chunker.pipeline import Pipeline

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chunker",
        description="Hierarchical document chunking with multi-level summaries",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Process a document")
    run_parser.add_argument("input_file", help="Path to input text file")
    run_parser.add_argument("--model", default=None, help="Model name")
    run_parser.add_argument("--output-dir", default=None, help="Output directory")

    resume_parser = subparsers.add_parser("resume", help="Resume from checkpoint")
    resume_parser.add_argument("checkpoint_file", help="Path to checkpoint file")
    resume_parser.add_argument("--output-dir", default=None, help="Output directory")

    return parser


def run_command(args: argparse.Namespace) -> None:
    input_path = Path(args.input_file)
    text = input_path.read_text()

    config_kwargs = {}
    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir
        config_kwargs["checkpoint_path"] = str(
            Path(args.output_dir) / "checkpoint.json"
        )

    if args.model:
        config = ChunkerConfig.from_model(args.model, **config_kwargs)
    else:
        config = ChunkerConfig(**config_kwargs)

    pipeline = Pipeline(config)
    result = pipeline.run(text, input_path.stem)

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

    config = ChunkerConfig(**config_kwargs)
    pipeline = Pipeline(config)
    result = pipeline.resume()

    logger.info(
        "Resumed: %d chunks, %d blocks, %d roots",
        result.total_chunks,
        result.total_blocks,
        len(result.root_block_ids),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        run_command(args)
    elif args.command == "resume":
        resume_command(args)


if __name__ == "__main__":
    main()
