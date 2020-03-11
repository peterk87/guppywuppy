#!/usr/bin/env python

import hashlib
import tempfile
from pathlib import Path
from typing import AsyncIterable

import httpx
from pyguppyclient import GuppyAsyncClientBase, yield_reads
from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse, json

import guppywuppy.default_settings


async def basecall_fast5(f5_path: str,
                         config: str = 'dna_r9.4.1_450bps_hac',
                         host: str = '127.0.0.1',
                         port: int = 5555) -> AsyncIterable[str]:
    async with GuppyAsyncClientBase(config=config,
                                    host=host,
                                    port=port) as client:
        n_reads = 0
        for read in yield_reads(f5_path):
            await client.pass_read(read)
            n_reads += 1
        logger.info(f'Passed all {n_reads} reads from "{f5_path}" to Guppy at {host}:{port}')
        done = 0
        samples = 0
        while done < n_reads:
            res = await client.get_called_read()
            if res is None:
                continue
            done += 1
            read, called = res
            samples += read.total_samples - called.trimmed_samples
            yield f'@{read.read_id}\n{called.seq}\n+\n{called.qual}'


def sha256_binary_file(path, buffer=1024 ** 2) -> str:
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(buffer)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


async def get_f5_data(f5id: int, host: str = 'localhost', port: int = 3000):
    uri = f'http://{host}:{port}/api/fast5/{f5id}'
    resp = await httpx.get(uri)
    f5_data = resp.json().get('data', {})
    return f5_data


app = Sanic('guppywuppy')
app.config.from_object(guppywuppy.default_settings)
app.config.load_environment_vars('GUPPYWUPPY_')


@app.route('/')
async def root(request: Request) -> HTTPResponse:
    logger.info(request.host)
    logger.info(request.headers)
    return json({'host': request.host,
                 'ip': request.remote_addr,
                 'port': request.port,
                 'url': request.url,
                 'args': request.args})


@app.route("/fast5")
async def test(request: Request) -> HTTPResponse:
    host = '127.0.0.1'
    port = 3000
    args = request.args
    logger.info(f'remote={request.remote_addr}')
    logger.info(f'args={args}')
    retries = 3
    f5id = args.get('id', [''])
    logger.info(f'FAST5 id={f5id}')

    try:
        f5id = int(f5id)
    except ValueError:
        return json({'error': f'Must provide valid integer id for FAST5. Provided id="{f5id}"'},
                    status=400)

    base_outdir = Path('/tmp/guppywuppy')
    base_outdir.mkdir(parents=True, exist_ok=True)
    logger.info(f'Getting FAST5 data for id={f5id} from {host}:{port}')
    f5_data = await get_f5_data(f5id, host, port)
    if f5_data is None or f5_data == {}:
        return json({'error': f'Could not retrieve info about FAST5 with id={f5id}'},
                    status=404)
    f5_filename = f5_data.get('filename', '')
    expected_sha256 = f5_data.get('sha256', '')
    if f5_filename == '' or expected_sha256 == '':
        return json({'error': f'FAST5 info map did not contain expected info: "{f5_data}"'},
                    status=404)
    logger.info(f'FAST5 id={f5id} filename="{f5_filename}" sha256="{expected_sha256}"')
    with tempfile.TemporaryDirectory() as tmpdir:
        uri = f'http://{host}:{port}/api/fast5/{f5id}/file'
        retry_count = 0
        while True:
            async with httpx.stream('GET', uri) as resp:
                count = 0
                f5_file = Path(tmpdir) / f5_filename
                with open(f5_file, 'wb') as fout:
                    async for chunk in resp.aiter_raw():
                        count += len(chunk)
                        fout.write(chunk)
            # check that sha256sum is okay
            f5_sha256 = sha256_binary_file(f5_file)
            if f5_sha256 == expected_sha256:
                break
            if retry_count >= retries:
                return json({'error': f'Could not download FAST5 id={f5id} from "{uri}". '
                                      f'SHA256 was "{f5_sha256}"; expected "{expected_sha256}"'},
                            status=500)

        fq_path = base_outdir / f'{f5_filename.replace(".fast5", "")}-{f5_sha256}.fastq'
        with open(fq_path, 'w') as fout:
            async for x in basecall_fast5(f5_file,
                                          config=app.config.GUPPY_CONFIG,
                                          port=app.config.GUPPY_PORT,
                                          host=app.config.GUPPY_HOST):
                fout.write(x)

    return json({"basecalled": True,
                 'fastq': str(fq_path),
                 'fastq_filesize': fq_path.lstat().st_size})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)
