workspace(name = "avatar_gen_attribute_api")

# Load the rules_docker repository and its dependencies.
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Declare the rules_docker repository which provides the oci_push rule.
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "b1e80761a8a8243d03ebca8845e9cc1ba6c82ce7c5179ce2b295cd36f7e394bf",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.25.0/rules_docker-v0.25.0.tar.gz"],
)

# Load and call the repositories function provided by rules_docker to fetch its dependencies.
load("@io_bazel_rules_docker//repositories:repositories.bzl", "repositories")
repositories()

# Load the language-specific rules and call their setup functions if necessary.
# For example, if you're using Python, you might need to call the python_repositories function.
# This step depends on the languages and tools you're using in your project.
