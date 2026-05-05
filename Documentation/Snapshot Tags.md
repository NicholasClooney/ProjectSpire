# Snapshot Tags

Read this before creating or reviewing snapshot tags.

Snapshot tags are annotated, date-based checkpoints named `snapshot/YYYY-MM-DD`.

To create the next snapshot:

1. Confirm the worktree is clean with `git status --short --branch`.
2. Review the previous snapshot with `git tag --list 'snapshot/*'` and `git show --no-patch snapshot/YYYY-MM-DD`.
3. Create an annotated tag:

```sh
git tag -a snapshot/YYYY-MM-DD -m "ProjectSpire snapshot YYYY-MM-DD" -m "Point-in-time snapshot of ProjectSpire work as of YYYY-MM-DD." -m "This is a baseline checkpoint, not a stable release." -m "Snapshot contents:" -m "- First notable change" -m "- Second notable change" -m "- Third notable change"
```

4. Push the tag with `git push origin snapshot/YYYY-MM-DD`.
