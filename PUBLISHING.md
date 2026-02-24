# Publishing to PyPI

This guide explains how to publish the `allegro-api` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - [PyPI](https://pypi.org/account/register/)
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)

2. **API Tokens**: Generate API tokens for both PyPI and TestPyPI:
   - Go to Account Settings → API tokens
   - Create a token with "Entire account" scope
   - Save tokens securely

3. **Configure `.pypirc`**:
   ```bash
   cp .pypirc.example ~/.pypirc
   ```
   Edit `~/.pypirc` and add your tokens:
   ```ini
   [pypi]
   username = __token__
   password = pypi-<your-token-here>
   
   [testpypi]
   username = __token__
   password = pypi-<your-test-token-here>
   ```

4. **Install Publishing Tools**:
   ```bash
   pip install --upgrade pip
   pip install --upgrade build twine
   ```

## Publishing Process

### 1. Update Version

Edit `pyproject.toml` and update the version number:
```toml
version = "0.1.1"  # Increment as needed
```

### 2. Update Changelog

Add a new entry to `CHANGELOG.md` describing the changes.

### 3. Run Tests

Ensure all tests pass:
```bash
make test
make lint
make type-check
```

### 4. Test on TestPyPI First

Always test on TestPyPI before publishing to production:

```bash
# Using the publish script
./scripts/publish.sh --test

# Or manually
make upload-test
```

Install and test from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ allegro-api
```

### 5. Publish to PyPI

Once tested, publish to production PyPI:

```bash
# Using the publish script
./scripts/publish.sh

# Or manually
make upload
```

### 6. Create GitHub Release

1. Push all changes:
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git push origin main
   ```

2. Create and push tag:
   ```bash
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin v0.1.1
   ```

3. Create GitHub release:
   - Go to GitHub → Releases → Create new release
   - Select the tag
   - Copy changelog entry as release notes
   - Publish release

## Using Makefile Commands

The Makefile provides convenient commands:

```bash
# Clean build artifacts
make clean

# Build package
make build

# Upload to TestPyPI
make upload-test

# Upload to PyPI
make upload

# Full release process (test, build)
make release
```

## Troubleshooting

### Authentication Issues
- Ensure your API token starts with `pypi-`
- Check that `.pypirc` has correct format
- Try using `--verbose` flag with twine for debugging

### Package Name Conflicts
- The package name must be unique on PyPI
- Consider using scoped names if needed

### Build Issues
- Ensure `pyproject.toml` is valid
- Check that all required files are included in `MANIFEST.in`
- Run `python -m build --help` for build options

## Best Practices

1. **Always test on TestPyPI first**
2. **Keep version numbers consistent** across:
   - `pyproject.toml`
   - `src/allegro_api/__init__.py`
   - Git tags
3. **Update documentation** for any API changes
4. **Run full test suite** before publishing
5. **Create detailed changelog entries**
6. **Tag releases in git**

## Automated Publishing (GitHub Actions)

For automated publishing, see `.github/workflows/publish.yml` (if configured).

## Post-Publishing Checklist

- [ ] Verify package on PyPI: https://pypi.org/project/allegro-api/
- [ ] Test installation: `pip install allegro-api`
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)
- [ ] Close related GitHub issues/PRs