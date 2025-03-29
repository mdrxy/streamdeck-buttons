# Template Information

[**Release notes**](https://github.com/fastapi/full-stack-fastapi-template/blob/master/release-notes.md)

## Updating From the Original Template

To get the latest changes from the original template:

1. Make sure you added the original repository as a remote; check by:

    ```sh
    git remote -v

    origin    git@github.com:octocat/my-full-stack.git (fetch)
    origin    git@github.com:octocat/my-full-stack.git (push)
    upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
    upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
    ```

2. Pull the latest changes ***without merging***:

    ```sh
    git pull --no-commit upstream master
    ```

    This will download the latest changes from this template without committing them, that way you can check everything is right before committing.

3. If there are conflicts, resolve them.

4. Once done, commit the changes:

    ```sh
    git merge --continue
    ```
