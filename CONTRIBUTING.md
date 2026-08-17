# Contributing to ALPS

<p align="right">
  <strong>English</strong> | <a href="docs/ja/CONTRIBUTING.md">Japanese</a>
</p>

Thank you for contributing to ALPS. Contributions are accepted under the repository license and the Developer Certificate of Origin 1.1 (DCO).

## Before You Contribute

- Read [LICENSE](LICENSE), [NOTICE](NOTICE), and [DCO](DCO).
- Keep English and Japanese counterparts aligned when a change affects both.
- Do not submit confidential information or material that you are not authorized to publish and license.
- Open an issue before a change that would alter ALPS semantics, Conformance requirements, or the license boundary.

## Developer Certificate of Origin

Every commit in a contribution must contain a `Signed-off-by` trailer from its contributor. The trailer certifies the statements in [DCO](DCO); it is not the same as a cryptographic commit signature.

Create the trailer with:

```console
git commit --signoff
```

The name and email in the trailer must identify the contributor and must match the authorship being certified. If a contribution contains work from another person, preserve that person's authorship and ensure that the DCO chain and applicable license permit the submission.

ALPS uses the DCO instead of a Contributor License Agreement. Contributors retain copyright in their contributions and license them under the license that applies to the contributed files.

## Third-Party Material

Contributors must identify the source, author, applicable license, and any permission for third-party material.

- Do not copy third-party text, figures, tables, examples, or translations unless the repository can retain documented authorization for the proposed use.
- A translation or close paraphrase can still depend on the source work. Do not label it an independent expression without checking the source and recording the basis for that classification.
- Mark quotations as quotations, keep them no longer than needed, and provide a precise source. Citation alone does not grant permission.
- For images, icons, and other assets, state who created them and confirm that the contribution can be distributed under the applicable repository license.
- Referencing a standard, book, product, organization, or trademark does not place the referenced material under the ALPS license.

Maintainers may request license evidence, written permission, or replacement of submitted material before accepting it.

## Preparing a Change

1. Work on a topic branch and keep unrelated changes separate.
2. Update the paired English or Japanese asset when required.
3. Preserve one authoritative source for each information item and use relative links from other documents.
4. Run the validation supplied by the affected Skill Package.
5. Run `git diff --check`, verify changed relative links, and inspect the final diff.
6. Commit with `--signoff`.

## Pull Request Checklist

- [ ] Every commit contains the required `Signed-off-by` trailer.
- [ ] I have the right to submit every part of the contribution under the applicable repository license.
- [ ] Third-party sources, permissions, quotations, and asset authorship are documented.
- [ ] English and Japanese counterparts have been assessed and updated where needed.
- [ ] Relevant checks pass, or the pull request explains why a check was not run.
