# create_embedded_pyc.py
import base64
import importlib.util
import os
import py_compile
import sys
import typing


class PycSource(typing.NamedTuple):
    b64_string: str
    header_length: int
    magic_bytes: bytes


def generate_embedded_pyc_string(source_py_path: str, display_name_for_pyc: str) -> typing.Optional[PycSource]:
    """
    Compiles a .py file to .pyc, reads its binary content,
    base64 encodes it, and returns the string along with the
    header length used for .pyc parsing.

    :param source_py_path): Path to the source .py file.
    :param display_name_for_pyc: The original name to associate w/ module (for tracebacks, etc.).
    :returns: Loaded data (or `None` if can't be loaded)
    """
    temp_pyc_file = f"_temp_{os.path.basename(source_py_path)}.pyc"
    header_length = -1

    try:
        # For Python 3.7+, CHECKED_HASH mode is common and results in a 16-byte header.
        # This header consists of:
        # 4 bytes: Magic Number (identifies Python version and .pyc format)
        # 4 bytes: Bitfield (flags indicating how the .pyc was compiled)
        # 8 bytes: Hash of the source file content
        # Following this header is the marshalled code object.
        py_compile.compile(
            source_py_path,
            cfile=temp_pyc_file,
            dfile=display_name_for_pyc,
            doraise=True,
            invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
        )
        header_length = 16

        with open(temp_pyc_file, "rb") as f_pyc:
            pyc_binary_content = f_pyc.read()

        # Capture the magic number from the generated .pyc
        # This should match importlib.util.MAGIC_NUMBER of the compiling Python
        original_magic_number = pyc_binary_content[:4]

        base64_encoded_pyc = base64.b64encode(pyc_binary_content).decode("utf-8")

        # Small verification
        if pyc_binary_content[:4] != importlib.util.MAGIC_NUMBER:
            print(
                "Warning: The magic number of the generated .pyc"
                " does not match the current Python interpreter's magic number."
                " This might be okay if compiled with a different patch version"
                " but could cause issues if major versions differ.",
                file=sys.stderr,
            )

        return PycSource(base64_encoded_pyc, header_length, original_magic_number)

    except Exception as e:
        print(f"Error during .pyc generation or encoding: {e}", file=sys.stderr)
        return None
    finally:
        if os.path.exists(temp_pyc_file):
            os.remove(temp_pyc_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <source_python_file.py>")
        sys.exit(1)

    source_file = sys.argv[1]
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        sys.exit(1)

    module_name = os.path.splitext(os.path.basename(source_file))[0]

    result = generate_embedded_pyc_string(source_file, source_file)

    if result:
        print(f"\n# --- Python {sys.version_info.major}.{sys.version_info.minor} ---")
        print(f"# --- Embedded PYC for module: {module_name} ---")
        print(f"# Original Magic Number: {result.magic_bytes.hex()}")
        print(f"# Assumed .pyc header length for loading: {result.header_length} bytes")
        print(f'\nEMBEDDED_PYC_MODULE_NAME = "{module_name}_embedded"')
        print(f"EMBEDDED_PYC_HEADER_LENGTH = {result.header_length}")
        print(f"EMBEDDED_PYC_MAGIC_NUMBER = {result.magic_bytes}")
        print(f'EMBEDDED_PYC_STRING = """\\\n{result.b64_string}\\\n"""')
        print("\n# Copy the lines above into top of test_runner.py")
