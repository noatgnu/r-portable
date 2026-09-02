# r-portable

Relocatable, CI-built R runtime archives, published as GitHub Releases.

`r-portable` builds R from its official CRAN source release, patches it (where necessary) to be fully relocatable, and publishes the result as a versioned archive so any tool can download, extract, and run R from an arbitrary directory with no system-wide install step.

## Release asset format

Each release ships, per platform/arch/R-version:

```
r-portable-<r-version>-<platform>-<arch>.<tar.xz|zip>
r-portable-<r-version>-<platform>-<arch>.<tar.xz|zip>.sha256
```

The `.sha256` sidecar contains a standard `sha256sum`-format line (`<hash>  <filename>`)
for integrity verification before extraction.

## How to use

In order to use the release, please fully extract the release anywhere on your system. However, the archive root itself is part of the distribution prefix that should not be changed unless you know what you are doing. The usual binaries that you will be interacting with is located at `bin/R` / `bin/Rscript` (`bin/R.exe` / `bin/Rscript.exe` on Windows) work immediately from that location with **no required environment variables**; each launcher locates its own `R_HOME` relative to itself.

### Recommended environment variables

None of these are required to launch R, but real consumers of these archives set them:

- `PATH` : add `<extracted-dir>/bin` so `R`/`Rscript` resolve by name instead of full path.
- `R_LIBS_USER` : set to a writable directory. Without it, `install.packages()` falls back to R's OS-default per-user library location, which lives outside the extracted tree and breaks portability. Packages installed there won't travel with the archive, and a second extraction elsewhere won't see them.
- `R_HOME` : not needed to launch R itself, but set it if you're invoking other tooling (e.g. compiling native R packages) that reads `R_HOME` from the environment instead of asking `R` directly.

## License

The build scripts and CI configuration in this repository are MIT licensed (see `LICENSE`).

**R itself is licensed under GPL-2/GPL-3.** Every published archive includes R's own `COPYING` file. Redistributing these builds does not change or relicense R.