#!/bin/bash
cd /home/kavia/workspace/code-generation/unified-jira-confluence-dashboard-170950-170959/backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

