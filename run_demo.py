import argparse

from visaflow.main import run_demo
from visaflow.config import SAMPLES_DIR


def list_samples():
    paths = sorted(SAMPLES_DIR.glob("*.txt"))
    if not paths:
        print("No sample files found.")
        return
    print("Available sample files:")
    for path in paths:
        print(f"- {path.name}")


def main():
    parser = argparse.ArgumentParser(description="Run the VisaFlow demo on a sample file.")
    parser.add_argument("filename", nargs="?", help="Sample filename in data/samples/")
    parser.add_argument("--list", action="store_true", help="List available sample files")
    parser.add_argument("--enhanced-draft", action="store_true", help="Use the enhanced local drafting mode")
    args = parser.parse_args()

    if args.list:
        list_samples()
        return

    filename = args.filename or "housing_email.txt"
    sample_path = SAMPLES_DIR / filename

    if not sample_path.exists():
        print(f"Sample file not found: {filename}")
        print("Use --list to see available files.")
        return

    print(run_demo(filename, enhanced_draft=args.enhanced_draft))


if __name__ == "__main__":
    main()
