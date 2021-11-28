import argparse
import sys

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create wiki js markdown page via graphql api.')

    # not sane default value, good for local development
    parser.add_argument(
        '--markdown-file',
        default='/data/projects/photoneo-test/documents/readme.md',
        help='Content of wiki page (markdown format)',
        nargs='?'
    )

    # not sane default value, good for local development
    parser.add_argument(
        '--api-endpoint-url',
        default='http://192.168.200.111/graphql',
        help='Url for wiki js graphql api endpoint e.g.: https://{host}/graphql',
        nargs='?'
    )

    parser.add_argument(
        '--token-file',
        default='../../workdir/wiki-js-token',
        help='File containing access token for graphql api',
        nargs='?'
    )

    parser.add_argument(
        '--graph-ql-create-page-template',
        default='./graphql_templates/create-page.template.txt',
        help='Template file containing mutation for page creation wiki js graphql api',
        nargs='?'
    )

    parser.add_argument(
        '--page-title',
        default='Home page',
        help='Title used for wiki page',
        nargs='?'
    )

    parser.add_argument(
        '--page-path',
        default='/home',
        help='Path on which page will be accessible /home',
        nargs='?'
    )

    return parser.parse_args()


def get_file_contents(file_line):
    file_handle = open(file_line, 'rt')
    result = []

    line = file_handle.readline()
    while line:
        result.append(line)
        line = file_handle.readline()

    file_handle.close()

    return "\n".join(result)


def get_graph_ql_client(token, api_endpoint_url):
    request_headers = {
        'Authorization': 'Bearer ' + token
    }

    transport = AIOHTTPTransport(
        url=api_endpoint_url,
        headers=request_headers,
    )

    return Client(transport=transport, fetch_schema_from_transport=True)


def create_page(graph_ql_client, create_page_graph_ql_template_file, title, path, content):
    template = get_file_contents(create_page_graph_ql_template_file)
    query = gql(template)

    data = {
        "content": content,
        "description": "Page created using graphql api via python gql",
        "editor": "markdown",
        "isPublished": True,
        "isPrivate": False,
        "locale": "en",
        "path": path,
        "tags": [],
        "title": title
    }

    try:
        response = graph_ql_client.execute(
            document=query,
            variable_values=data
        )

        print(response)
    except Exception as e:
        print('Error %s' % e)
        sys.exit(1)


def main():
    arguments = parse_arguments()

    token = get_file_contents(arguments.token_file)
    graph_ql_client = get_graph_ql_client(token, arguments.api_endpoint_url)

    create_page(
        graph_ql_client,
        arguments.graph_ql_create_page_template,
        arguments.page_title,
        arguments.page_path,
        get_file_contents(arguments.markdown_file)
    )


main()
