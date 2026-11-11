#!/usr/bin/env python3
"""Download a public source once and verify its declared file type before saving."""

import argparse
import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def validate_payload(data, expected, content_type=''):
    if not data:
        raise ValueError('Empty response')
    prefix = data[:1024].lstrip().lower()
    html = prefix.startswith((b'<!doctype html', b'<html')) or 'text/html' in content_type.lower()
    if expected == 'pdf':
        if not data[:1024].lstrip().startswith(b'%PDF-') or html:
            raise ValueError('Expected PDF; response has no PDF header or is an HTML/interstitial page')
    elif expected in ('text', 'csv', 'json'):
        if html:
            raise ValueError('Expected ' + expected + '; received HTML/interstitial page')
        text = data.decode('utf-8-sig')
        if expected == 'json':
            json.loads(text)
        elif expected == 'csv':
            rows = csv.reader(io.StringIO(text))
            header = next(rows, [])
            first = next(rows, [])
            if len(header) < 2 or len(first) != len(header):
                raise ValueError('Expected tabular CSV header and at least one row')
    elif expected == 'html':
        if not html:
            raise ValueError('Expected HTML')
    else:
        raise ValueError('Unknown expected type')
    return {'type_checked': True, 'identity_checked': False, 'fulltext_checked': False}


def download(url, output, expected, max_bytes=20 * 1024 * 1024):
    output = Path(output)
    if output.exists():
        raise ValueError('Output exists; use a new versioned filename')
    if not url.startswith('https://'):
        raise ValueError('Use the actual public HTTPS source URL')
    record = {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'expected': expected}
    request = urllib.request.Request(url, headers={'User-Agent': 'AcademicWritingHarness/0.2 (research)'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read(max_bytes + 1)
            record.update({'http_status': response.status, 'final_url': response.url,
                           'content_type': response.headers.get('Content-Type', ''), 'bytes': len(data)})
        if len(data) > max_bytes:
            raise ValueError('Source exceeds declared retrieval size limit')
        record.update(validate_payload(data, expected, record['content_type']))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as handle:
            handle.write(data)
        record.update({'saved': True, 'path': str(output)})
    except (OSError, ValueError, UnicodeError) as error:
        record.update({'saved': False, 'error': str(error)})
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--output', required=True)
    parser.add_argument('--expected', choices=('pdf', 'html', 'text', 'csv', 'json'), required=True)
    args = parser.parse_args()
    try:
        result = download(args.url, args.output, args.expected)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result['saved'] else 2)
    except (OSError, ValueError) as error:
        print(json.dumps({'saved': False, 'error': str(error)}, ensure_ascii=False))
        sys.exit(2)
