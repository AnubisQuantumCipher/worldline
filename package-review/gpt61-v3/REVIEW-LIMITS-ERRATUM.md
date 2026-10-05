# Create-only review limits erratum

This corrects the review-method statement in REVIEW.md; it does not change any package/design finding, closure status or verdict.

During final artifact metadata reporting, the reviewer used `Path('REVIEW.md').resolve()` to print an absolute path. The installed standard-library implementation calls os.path.realpath, whose component walk calls lstat; this includes the ancestor `/home/sicarii`. That breached the user's explicit prohibition on statting that directory. The command returned. It did not enumerate or read the directory's contents or access either iPad mount or the SIA brain. No further Path.resolve/realpath calls will be used in this review's remaining commands.

The REVIEW.md sentence claiming no forbidden home-root path was listed or read must be interpreted with this explicit correction: no forbidden directory listing/content access occurred, but this ancestor metadata read did occur. Review.md is create-only and has not been rewritten. checks.json and review.json bind this erratum and record the failed procedural constraint. All original obligations, approval/proof/source/Phase One acceptance fields, and the NOT_READY verdict remain unchanged.

Read-only implementation evidence: `/usr/lib/python3.14/pathlib/__init__.py:932-938` calls os.path.realpath; `/usr/lib/python3.14/posixpath.py:457` performs lstat(newpath). No test or reproduction was run to make this determination.
