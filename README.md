# what-changed

Trivial scripts for reviewing Cinnamon and Pantheon (probably some other random packages) Nixpkgs pull requests. Some upstream release notes do not really mention what you should address in your Nixpkgs pull request so I set up this workflow to read all the diffs when possible.

For GNOME Nixpkgs pull requests, consider [jtojnar/what-changed](https://github.com/jtojnar/what-changed) (for reading NEWS) and [jtojnar/nonemast](https://github.com/jtojnar/nonemast) (for tracking review status).

### Usage

You don't need to run anything locally, all outputs are updated regularly by GitHub actions.

- [000-test.md](000-test.md): Trivial config for testing purpose only.
- [001-pantheon.md](001-pantheon.md): elementary OS / Pantheon packages.
- [002-maintained.md](002-maintained.md): Random third-party packages, mostly Pantheon related.
- [003-cinnamon.md](003-cinnamon.md): Linux Mint / Cinnamon packages.

Copy the entries you need, paste them as an issue or a comment, then go through the list.
