# Contributing to ALPS

<p align="right">
  <strong>English</strong> | <a href="docs/locales/ja/CONTRIBUTING.md">Japanese</a>
</p>

Contributions are accepted under the repository license and the [Developer Certificate of Origin 1.1](DCO).

## Before Contributing

- Read [LICENSE](LICENSE), [NOTICE](NOTICE), [DCO](DCO), and [AGENTS.md](AGENTS.md).
- Keep changed English and Japanese counterparts semantically aligned.
- Do not submit confidential information or material that you are not authorized to publish and license.
- Discuss changes that would alter the single-Skill product boundary, public behavior, or license boundary before implementation.

## Certificate and Rights

Every contributed commit must contain the contributor's `Signed-off-by` trailer. Create it with:

```console
git commit --signoff
```

The trailer certifies the statements in [DCO](DCO); it is not a cryptographic signature. Preserve other authors' authorship and ensure the DCO chain and applicable license permit submission.

Identify the source, author, license, and permission for third-party material. Do not copy text, figures, examples, translations, or assets unless the repository can document and distribute the proposed use. Keep quotations no longer than needed and provide a precise source. Citation alone does not grant permission.

## Prepare and Validate a Change

1. Work on a topic branch and keep unrelated changes separate.
2. Update affected English and Japanese counterparts.
3. Keep one authoritative source for each information item and use relative links from other files.
4. Run the official validation for `skills/design-process-description`, manifest and Host checks, repository tests, relative-link checks, and `git diff --check` as applicable.
5. Inspect the complete final diff.
6. Commit with `--signoff`.

When proposing a change, report checks that passed and any check that could not be run.
