from flask import Flask, request, jsonify
from flask_restful import reqparse, abort
from git import Repo, GitCommandError
import os
import base64
import shutil

app = Flask(__name__)

@app.route('/api/interact-with-repo', methods=['POST'])
def interact_with_repo():
    # Define the parser for validating incoming request data
    parser = reqparse.RequestParser()
    parser.add_argument('repo_url', required=True, type=str, help='URL of the GitHub repository')
    parser.add_argument('local_dir', required=True, type=str, help='Local directory to clone the repository to')
    parser.add_argument('file_path', required=True, type=str, help='Path of the file in the repository to modify')
    parser.add_argument('file_content', required=True, type=str, help='New content for the file')
    parser.add_argument('commit_message', required=True, type=str, help='Commit message for the changes')

    # Parse the incoming request data
    args = parser.parse_args()

    try:
        # Clone the repository
        if not os.path.exists(args.local_dir):
            os.makedirs(args.local_dir)
        repo = Repo.clone_from(args.repo_url, args.local_dir)

        # Modify the file
        file_path = os.path.join(args.local_dir, args.file_path)
        with open(file_path, 'w') as file:
            file.write(base64.b64decode(args.file_content).decode('utf-8'))

        # Commit the changes
        repo.git.add(update=True)
        repo.index.commit(args.commit_message)

        # Push the changes
        origin = repo.remote(name='origin')
        origin.push()

        # Delete the local copy of the repository
        shutil.rmtree(args.local_dir)

        return jsonify({'status': 'success'})
    except GitCommandError as e:
        abort(400, message=f'Error interacting with the GitHub repository: {str(e)}')
    except Exception as e:
        abort(500, message=f'Unexpected error: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)
