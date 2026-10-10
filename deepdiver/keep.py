"""
Keep a download in a git repository that is never rewound.

A Miadi Chronicle episode keeps a notebook's media in git, and git keeps every
byte for good there. `studio download --keep` (or `studio keep <dir>`) turns a
download folder into what the episode commits:

- an infographic PNG becomes WebP at quality 90 without metadata, and the PNG
  is removed (Episode 140's went from 4.5 MB to 280 KB);
- a video or audio overview is re-encoded into `keep/`, the only place the
  chronicle's .gitignore lets `.mp4` and `.m4a` in (Episode 140's 31 MB video
  became 6.5 MB). The download stays beside it, out of git;
- reports are kept as they are.

Each entry of manifest.json gains `kept`: the path relative to the folder, its
size and sha256, and how it was made. The download's own `path`, `size` and
`sha256` stay as they were, so the manifest says both what Gemini Notebook gave
and what the episode keeps (miadi-chronicle://251, finding F8 of the first
/deepdive run).
"""

import hashlib
import json
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm')
AUDIO_EXTENSIONS = ('.m4a', '.mp3', '.wav')

WEBP_HOW = 'WebP, quality 90, no metadata (ffmpeg libwebp)'
VIDEO_HOW = 'H.264 CRF 30 preset slow tune stillimage, AAC 64 kb/s, faststart, no metadata (ffmpeg)'
AUDIO_HOW = 'AAC 64 kb/s, faststart, no metadata (ffmpeg)'


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _run_ffmpeg(args: List[str]) -> Optional[str]:
    """Run ffmpeg; return None on success, or its error text."""
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        return 'ffmpeg not found'
    proc = subprocess.run([ffmpeg, '-v', 'error', '-y', *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return (proc.stderr or f'ffmpeg exit {proc.returncode}').strip()[-400:]
    return None


def _kept_record(folder: str, path: str, how: str) -> Dict[str, Any]:
    return {
        'path': os.path.relpath(path, folder),
        'size': os.path.getsize(path),
        'sha256': _sha256(path),
        'how': how,
    }


def keep_entry(entry: Dict[str, Any], folder: str) -> Dict[str, Any]:
    """Make the kept form of one manifest entry. Returns the entry, updated."""
    # studio download writes every file into the folder itself, and the manifest
    # holds absolute paths of the host that downloaded. Read by name, so a folder
    # that moved, or was cloned on another host, still resolves.
    source = os.path.join(folder, os.path.basename(entry.get('path') or ''))
    ext = os.path.splitext(source)[1].lower()

    if entry.get('kept') and os.path.exists(os.path.join(folder, entry['kept']['path'])):
        return entry  # already kept by an earlier run

    if entry.get('html_path') or ext in ('.md', '.html'):
        entry['kept'] = _kept_record(folder, source, 'as downloaded')
        return entry

    stem = os.path.splitext(os.path.basename(source))[0]
    targets = {
        **{e: (os.path.join(folder, f'{stem}.webp'), WEBP_HOW) for e in IMAGE_EXTENSIONS},
        **{e: (os.path.join(folder, 'keep', f'{stem}.mp4'), VIDEO_HOW) for e in VIDEO_EXTENSIONS},
        **{e: (os.path.join(folder, 'keep', f'{stem}.m4a'), AUDIO_HOW) for e in AUDIO_EXTENSIONS},
    }
    if ext in targets and os.path.exists(targets[ext][0]):
        # Kept already, by hand or by an earlier version: record it, never redo it.
        target, how = targets[ext]
        entry['kept'] = _kept_record(folder, target, how + '; made before this run')
        return entry

    if not os.path.exists(source):
        entry['kept_error'] = 'download not on disk'
        return entry

    if ext in IMAGE_EXTENSIONS:
        target = os.path.join(folder, f'{stem}.webp')
        error = _run_ffmpeg(['-i', source, '-c:v', 'libwebp', '-quality', '90',
                             '-map_metadata', '-1', target])
        if error:
            entry['kept_error'] = error
            return entry
        entry['kept'] = _kept_record(folder, target, WEBP_HOW)
        os.remove(source)
        return entry

    if ext in VIDEO_EXTENSIONS or ext in AUDIO_EXTENSIONS:
        keep_dir = os.path.join(folder, 'keep')
        os.makedirs(keep_dir, exist_ok=True)
        if ext in VIDEO_EXTENSIONS:
            target = os.path.join(keep_dir, f'{stem}.mp4')
            args = ['-i', source, '-c:v', 'libx264', '-preset', 'slow', '-crf', '30',
                    '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '64k',
                    '-movflags', '+faststart', '-map_metadata', '-1', target]
            how = VIDEO_HOW
        else:
            target = os.path.join(keep_dir, f'{stem}.m4a')
            args = ['-i', source, '-vn', '-c:a', 'aac', '-b:a', '64k',
                    '-movflags', '+faststart', '-map_metadata', '-1', target]
            how = AUDIO_HOW
        error = _run_ffmpeg(args)
        if error:
            entry['kept_error'] = error
            return entry
        entry['kept'] = _kept_record(folder, target, how)
        return entry

    entry['kept'] = _kept_record(folder, source, 'as downloaded')
    return entry


def keep_folder(folder: str) -> Dict[str, Any]:
    """Apply keep_entry to every download in <folder>/manifest.json and rewrite it."""
    manifest_path = os.path.join(folder, 'manifest.json')
    with open(manifest_path, encoding='utf-8') as fh:
        manifest = json.load(fh)
    for entry in manifest.get('downloads', []):
        keep_entry(entry, folder)
    with open(manifest_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    return manifest
