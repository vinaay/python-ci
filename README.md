# 01_03 Set Up CI for Python

When you run tests in GitHub Actions, the results aren’t always easy to find. Test output is often buried inside individual workflow steps, which means you have to expand logs and scroll around just to understand what passed or failed.

Many testing frameworks—including Pytest—can help with this by generating **JUnit reports**.

added the additional package in the requirement.txt

JUnit is a standard test reporting format that summarizes all the tests that were executed and clearly shows which tests passed and which failed. Instead of digging through raw logs, these reports give you a structured view of your test results.

In this lab, you’ll make test results more visible by publishing JUnit reports directly to the GitHub Actions interface.

You’ll start by updating the workflow’s job permissions so it’s allowed to publish test reports. Next, you’ll modify the Pytest command to generate JUnit output files. Finally, you’ll add an action that reads those files and publishes the results as part of the workflow run.

To do this, you’ll use the **JUnit Report** action from the GitHub Actions Marketplace, turning your starter workflow into a more informative and developer-friendly CI pipeline.

## References

| Reference                                                                                                        | Description                                              |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [actions/setup-python on GitHub Marketplace](https://github.com/marketplace/actions/setup-python)                | GitHub Action for setting up Python environments         |
| [mikepenz/action-junit-report on GitHub Marketplace](https://github.com/marketplace/actions/junit-report-action) | GitHub Action for publishing JUnit test reports          |
| [actions/checkout on GitHub Marketplace](https://github.com/marketplace/actions/checkout)                        | GitHub Action for checking out repository code           |
| [Documentation for the Python project used for this lesson](./PY_PROJECT_DETAILS.md)                             | Documentation for the Python project used in this lesson |
| [The updated workflow for this lesson](./py-ci-workflow.yml)                                                     | The complete workflow file for this lesson               |

## Lab: Publish Test Results in GitHub Actions

In this lab, you’ll start with a GitHub starter workflow for a Python project and improve it by publishing test results directly to the workflow summary using JUnit reports.

By the end of this lab, test results will be easy to find without digging through workflow logs.

### Prerequisites

Before starting this lab, make sure you have:

- A new GitHub repository
- The Python project files from this lesson committed to the repository

### Instructions

#### 1. Create a Starter Workflow for a Python Project

1. Open your repository in GitHub.
2. Select the **Actions** tab.
3. Review the workflows GitHub suggests based on the files in your repository.
4. Locate **Python application** and select **Configure**.

GitHub creates a starter workflow that includes steps to:

- Check out the repository
- Set up Python 3.10
- Install dependencies
- Lint the code with Flake8
- Run tests with Pytest

#### 2. Review the Starter Workflow

Take a moment to review the workflow file:

- The **checkout** step pulls your code into the runner.
- The **setup-python** step configures Python version 3.10.
- Dependencies are installed using `pip`, including Flake8 and Pytest.
- Flake8 runs to lint the code.
- Pytest runs to execute the test suite.

1. Commit the workflow file to the `main` branch.
2. After the commit completes, select the **Actions** tab.
3. Open the workflow run that was triggered by the commit.

The workflow should complete successfully.

#### 3. Review Test Results in the Workflow Logs

1. Open the **build** job.
2. Select the step named **Test with pytest**.
3. Scroll through the logs to find the test output.

Notice that:

- Test results are present
- You must expand steps and scroll logs to find them

Next, you’ll improve this experience by publishing test results to the workflow summary.

#### 4. Edit the Workflow File

1. From the workflow run, select **Workflow file**.
2. Select the pencil icon to edit the workflow.

#### 5. Add Permissions to Publish Test Results

To allow the workflow to publish test reports, update the job permissions.

Under the existing `permissions` section, add `checks: write`:

```yaml
permissions:
  contents: read
  checks: write
```

This gives the workflow permission to write test results to the Actions interface.

#### 6. Update Pytest to Generate JUnit Reports

1. Open the `README.md` file in your repository.
2. Replace the existing Pytest step:

   ```yaml
   - name: Test with pytest
   run: |
       pytest
   ```

   With the following:

   ```yaml
   - name: Test with pytest
   run: |
       python -m pytest --verbose --junit-xml=junit.xml
   - name: Publish Test Report
   uses: mikepenz/action-junit-report@v3
   if: success() || failure()
   with:
       report_paths: '**/junit.xml'
       detailed_summary: true
       include_passed: true
   ```

   This change does two things:

   - Pytest now generates a JUnit XML report
   - The JUnit Report action publishes the results to the workflow summary

3. Commit the changes to the workflow file.

#### 7. Review Published Test Results

1. Select the **Actions** tab.
2. Open the latest workflow run.
3. Wait for the job to complete.

When the run finishes, review the **Summary** page.

You should now a chart of passed, failed, and skipped tests displayed directly on the workflow summary page.

![JUnit Test Report Summary](images/01_03-junit-report.png)

### Summary

Most modern test frameworks can produce JUnit reports, making this approach a powerful way to improve visibility and feedback in your CI pipelines.

## <!-- FooterStart -->

[← 01_02 Set Up CI for Javascript](../01_02_set_up_ci_for_javascript/README.md) | [01_04 Set Up CI for Go →](../01_04_set_up_ci_for_go/README.md)

<!-- FooterEnd -->
