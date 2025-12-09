import hashlib
import os
from pathlib import Path
from typing import Dict, List, Tuple


BUFFER_SIZE_BYTES = 1024 * 1024  # 1 MiB


def compute_file_hash(file_path: Path) -> str:
	"""Compute SHA-256 hash of a file in a memory-efficient streaming manner."""
	hasher = hashlib.sha256()
	with file_path.open('rb') as f:
		while True:
			chunk = f.read(BUFFER_SIZE_BYTES)
			if not chunk:
				break
			hasher.update(chunk)
	return hasher.hexdigest()


def gather_files(root: Path) -> Dict[str, Path]:
	"""Recursively gather all files under root, mapping normalized relative path -> absolute Path.

	Normalization rules:
	- Use POSIX-style separators for the relative key to keep consistent across platforms
	- On Windows, keys are case-insensitive, so store lower-cased keys
	"""
	if not root.exists():
		raise FileNotFoundError(f"路径不存在: {root}")
	if not root.is_dir():
		raise NotADirectoryError(f"不是文件夹: {root}")

	files: Dict[str, Path] = {}
	for abs_path in root.rglob('*'):
		if abs_path.is_file():
			rel = abs_path.relative_to(root).as_posix()
			key = rel.lower() if os.name == 'nt' else rel
			files[key] = abs_path
	return files


def compare_directories(dir_a: Path, dir_b: Path) -> Tuple[bool, List[str]]:
	"""Compare files from dir_a against dir_b by relative path and content.

	Returns (all_present_and_equal, diff_messages)
	"""
	files_a = gather_files(dir_a)
	files_b = gather_files(dir_b)

	diffs: List[str] = []
	all_ok = True

	for rel_key, path_a in files_a.items():
		path_b = files_b.get(rel_key)
		# Reconstruct a printable relative path preserving original case from A
		rel_display = path_a.relative_to(dir_a).as_posix()

		if path_b is None:
			all_ok = False
			diffs.append(f"缺失: B 中不存在文件 {rel_display}")
			continue

		# Quick size check first
		size_a = path_a.stat().st_size
		size_b = path_b.stat().st_size
		if size_a != size_b:
			all_ok = False
			diffs.append(
				f"不同: {rel_display} 大小不一致 (A: {size_a} B: {size_b})"
			)
			continue

		# Same size, compare hash
		hash_a = compute_file_hash(path_a)
		hash_b = compute_file_hash(path_b)
		if hash_a != hash_b:
			all_ok = False
			diffs.append(f"不同: {rel_display} 内容哈希不一致")

	return all_ok, diffs


def prompt_for_path(prompt_text: str) -> Path:
	while True:
		user_input = input(prompt_text).strip().strip('"').strip("'")
		if not user_input:
			print("输入不能为空，请重试。")
			continue
		p = Path(user_input).expanduser().resolve()
		if not p.exists():
			print(f"路径不存在: {p}")
			continue
		if not p.is_dir():
			print(f"不是文件夹: {p}")
			continue
		return p


def main() -> None:
	print("请输入两个需要比较的文件夹路径：")
	dir_a = prompt_for_path("A 路径: ")
	dir_b = prompt_for_path("B 路径: ")

	print("\n开始比较，请稍候...\n")
	all_ok, diffs = compare_directories(dir_a, dir_b)

	if all_ok:
		print("结果: 是。A 中的所有文件都在 B 中，且内容一致。")
	else:
		print("结果: 否。存在以下差异：")
		for msg in diffs:
			print(f"- {msg}")


if __name__ == "__main__":
	main()


