"""Test script."""

import os
import stat
import shutil
import subprocess
import time

TEST_PATH = './gtm_tests/'
GTM_PATH = '../build/go_build_github_com_kilpkonn_gtm_enhanced'
TEST_FILE_NAME = 'test.txt'


def setup():
    """Setup tests."""
    shutil.copyfile(GTM_PATH, 'gtm')
    st = os.stat('gtm')
    os.chmod('gtm', st.st_mode | stat.S_IEXEC)
    subprocess.call(['git', 'init'])
    with open(TEST_FILE_NAME, 'w') as f:
        f.write("0")
    subprocess.call(['git', 'add', '.'])
    subprocess.call(['git', 'commit', '.', '-m "test"'])


def cleanup():
    """Clean tests"""
    os.chdir('..')
    shutil.rmtree(TEST_PATH, ignore_errors=True)
    os.makedirs(TEST_PATH, exist_ok=True)
    os.chdir(TEST_PATH)


def get_size(start_path: str = '.'):
    total_size = 0
    for dir_path, dir_names, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def test_commit_benchmark(n: int):
    """Test commit 10000 times"""
    for i in range(n):
        with open(TEST_FILE_NAME, 'w') as f:
            f.write(str(i))
        subprocess.call(['git', 'commit', '.', '-m "test"'], )


def test_commit_gtm(n: int):
    """Test commit 10000 times"""
    for i in range(n):
        with open(TEST_FILE_NAME, 'w') as f:
            f.write(str(i))
        subprocess.call(['./gtm', 'record', TEST_FILE_NAME])
        subprocess.call(['git', 'commit', '.', '-m "test"'])


def test_commit_increasing_size_benchmark(n: int, increase_multiplier: float):
    """Test commit 10000 times with increasing file size."""
    for i in range(n):
        with open(TEST_FILE_NAME, 'a') as f:
            new_text = ''.join([f'{n} - {x}\n' for x in range(round(i * increase_multiplier))])
            f.write(new_text)
        subprocess.call(['git', 'commit', '.', '-m "test"'])


def test_commit_increasing_size_gtm(n: int, increase_multiplier: float):
    """Test commit 10000 times with increasing file size."""
    for i in range(n):
        with open(TEST_FILE_NAME, 'a') as f:
            new_text = ''.join([f'{n} - {x}\n' for x in range(round(i * increase_multiplier))])
            f.write(new_text)

        for _ in range(round(i * increase_multiplier)):
            subprocess.call(['./gtm', 'record', TEST_FILE_NAME])
        subprocess.call(['git', 'commit', '.', '-m "test"'])


def test_commit_record_gtm(n: int):
    """Test commit 10000 times"""
    for i in range(n):
        subprocess.call(['./gtm', 'record', TEST_FILE_NAME])


if __name__ == '__main__':
    os.makedirs(TEST_PATH, exist_ok=True)
    os.chdir(TEST_PATH)

    results = ['Results:']

    setup()
    start_benchmark = time.time()
    test_commit_benchmark(2000)
    end_benchmark = time.time()
    size_benchmark = get_size('.git')
    cleanup()

    setup()
    start_gtm = time.time()
    test_commit_gtm(2000)
    end_gtm = time.time()
    size_gtm = get_size('.git')
    cleanup()

    results.append('-' * 50)
    results.append(f'2000 commits Benchmark time: {round(end_benchmark - start_benchmark, 2)}s')
    results.append(f'2000 commits Gtm time: {round(end_gtm - start_gtm, 2)}s')
    results.append(f'Benchmark .git folder size: {round(size_benchmark / 1024, 2)} kB')
    results.append(f'Gtm .git folder size: {round(size_gtm / 1024, 2)} kB')

    setup()
    start_benchmark = time.time()
    test_commit_increasing_size_benchmark(100, 1.5)
    end_benchmark = time.time()
    size_benchmark = get_size('.git')
    cleanup()

    setup()
    start_gtm = time.time()
    test_commit_increasing_size_gtm(100, 1.5)
    end_gtm = time.time()
    size_gtm = get_size('.git')
    cleanup()

    results.append('-' * 50)
    results.append(f'100 commits inc size Benchmark time: {round(end_benchmark - start_benchmark, 2)}s')
    results.append(f'100 commits inc size (7500 record events) Gtm time: {round(end_gtm - start_gtm, 2)}s')
    results.append(f'Benchmark .git folder size: {round(size_benchmark / 1024, 2)} kB')
    results.append(f'Gtm .git folder size: {round(size_gtm / 1024, 2)} kB')

    setup()
    start_gtm = time.time()
    test_commit_record_gtm(100 * 75)
    end_gtm = time.time()
    cleanup()

    results.append(f'7500 record event time: {round(end_gtm - start_gtm, 2)}s')

    for line in results:
        print(line)