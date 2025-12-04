import hashlib
from pathlib import Path
import re


def hash_path(path: Path,n_hash:int=None,n_parents:int=3) -> str:
    """
    Generate a hash for the given path.

    Args:
        path (str): The file path to hash.

    Returns:
        str: A hexadecimal string representing the hash of the path.
    """
    import hashlib

    # Create a SHA-256 hash object
    hasher = hashlib.sha256()
    path = Path(path)
    # Update the hash object with the bytes of the path
    p = path.resolve().as_posix()
    hasher.update(p.encode('utf-8' ))
    # Return the hexadecimal digest of the hash
    result = hasher.hexdigest()[slice(0, n_hash)]
    # Add explit part
    real_n_parents = len(path.parts) -1 # -1 pour ne pas avoir la racine par exemple c:\
    result = result + "_" + "_".join(path.parts[-(min(real_n_parents, n_parents)):])
    return sanitize_path_part(result, extra_prohibited_chars="\.")

def hash_file_content(path: Path) -> str:
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def resolve_path(path:Path,relative_to:Path=None):
    path = Path(path)
    if relative_to is  None:
        return path.resolve()
    relative_to = Path(relative_to)
    return Path(*relative_to.parts,*path.parts).resolve()

def has_been_modified(path:Path, reference:Path,hash:bool=False):
    if not path.exists() or not reference.exists():
        return True
    if not hash:
        return (path.stat().st_mtime > reference.stat().st_mtime)
    return hash_file_content(path) != hash_file_content(reference)

def sanitize_path_part(path_part: str,extra_prohibited_chars: str="") -> str:
    """
    Remove or replace prohibited symbols from a path part.
    
    Args:
        path_part (str): The path part to sanitize
        extra_prohibited_chars (str): Additional characters to treat as prohibited sa regular expression.
        
    Returns:
        str: Sanitized path part safe for use in filenames
    """
    # Define prohibited characters for Windows/Unix file systems
    prohibited_chars = r'<>:"/\\|?*\x00-\x1f'
    prohibited_chars += extra_prohibited_chars
    prohibited_chars = rf'[{prohibited_chars}]'

    # Replace prohibited characters with underscores
    clean_part = re.sub(prohibited_chars, '_', path_part)
    
    # Remove leading/trailing dots and spaces (Windows doesn't like these)
    clean_part = clean_part.strip('. ')
    
    # Handle reserved Windows names
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if clean_part.upper() in reserved_names:
        clean_part = clean_part + '_'
    
    # Ensure the result is not empty
    if not clean_part:
        clean_part = 'unnamed'
    
    return clean_part

if __name__ == "__main__":
    print(resolve_path(Path.home(),Path.cwd()))
    print(resolve_path("..",Path.cwd()))
    print(resolve_path(Path.cwd(),Path.home()))
    print(resolve_path("..",Path.home()))