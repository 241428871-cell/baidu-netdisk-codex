---
name: organize-netdisk-books
description: Copy and deduplicate a Baidu Netdisk book collection into a readable mirrored folder hierarchy, favoring text-convertible formats.
---

# Organize Baidu Netdisk books

Use this workflow when the user asks to organize a large book collection in
Baidu Netdisk. Confirm the source and destination paths and whether the user
wants copy or move. Preserve the source when the request says copy.

1. Recursively inventory the source with complete pagination. Keep each
   file's path, ID, size, extension, and parent folder. Save a resumable scan
   checkpoint. Do not treat an incomplete scan as a complete library.
2. Exclude manga and comics, including comic archive extensions and clear
   manga/comic folder or title markers. Exclude videos. Audio files and other
   nontext media are not candidates for a .txt-convertible book.
3. Normalize titles conservatively: remove format and language labels and
   duplicate-copy suffixes, while retaining author, volume, and edition
   distinctions. Group by normalized title and language. Keep a Chinese
   translation and English original separately when both exist.
4. Pick one file per group. Prefer an existing .txt, then Markdown or
   HTML, EPUB, FB2, RTF, DOCX, ODT, DOC, TeX, MOBI, AZW3, AZW, PRC, CHM,
   DJVU, and PDF. If the best copy is corrupt or visibly incomplete,
   inspect candidates and choose a usable copy. Record selection and skip
   reasons in a plan before copying.
5. Recreate the selected files' relative source folders under the target.
   Check for an existing folder before creation; avoid automatic rename
   suffixes. Copy in small batches, checkpoint progress, and inspect both
   batch and per-file response errors. On frequency control, pause and lower
   concurrency, then resume.
6. Verify all planned files are present at their destination path and that
   the source still exists when copying. Report unresolved files explicitly.

For a large library, build and execute the inventory and plan in a local
script. Store inventories, plans, and execution state outside this public
plugin source tree, because file names can be private.
