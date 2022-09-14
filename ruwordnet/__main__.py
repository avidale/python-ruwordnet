import argparse
import os
import urllib.request


URLS = {
    '2020': 'https://github.com/avidale/python-ruwordnet/releases/download/0.0.2/ruwordnet.db',
    '2021': 'https://github.com/avidale/python-ruwordnet/releases/download/0.0.4/ruwordnet-2021.db',
}


def main():
    parser = argparse.ArgumentParser(description='Tools for RuWordNet')
    subparsers = parser.add_subparsers(dest='subparser')
    download = subparsers.add_parser('download', help='Download the model')
    download.add_argument('-u', '--url', default=URLS['2021'], help='url of the model to download')
    args = parser.parse_args()
    if args.subparser == 'download':
        dirname = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        destination = os.path.join(dirname, 'ruwordnet.db')
        print('downloading a ruwordnet model from', args.url)
        urllib.request.urlretrieve(args.url, destination)


if __name__ == '__main__':
    main()
