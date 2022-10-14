const scope = [
    "confirm",
    "form",
    "toolchain"
]

module.exports = {
    extends: ['@commitlint/config-angular'],
    rules: {
        'scope-enum': [2, 'always', scope]
    }
};
