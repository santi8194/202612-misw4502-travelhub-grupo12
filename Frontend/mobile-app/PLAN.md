# Plan - DevOps/CI-CD Implementation

This plan outlines the steps to implement a robust CI/CD pipeline for the Travel Hub Mobile project, focusing exclusively on Android and using a team of agents to ensure code quality and build verification.

## Context
The project requires an automated CI/CD workflow to ensure code quality through static analysis, unit testing, and Android build verification.

## Approach
1.  **Form an Agent Team**: Use a team of specialized agents (Logic/ViewModel, QA/Test, DevOps/CI-CD) to collaborate on the implementation.
2.  **DevOps/CI-CD Implementation**: Create a GitHub Actions workflow (`.github/workflows/android_ci.yml`) for:
    -   Installing Flutter dependencies.
    -   Static analysis (`flutter analyze`).
    -   Unit and widget tests (`flutter test`).
    -   Android Release Build verification.
3.  **Android Signing**: Configure the project to use GitHub Secrets for signing release builds (Keystore, Store Password, Key Alias, Key Password).
4.  **Local Verification**: Ensure all scripts and build commands pass locally using the `flutter` and `gradle` toolchains before pushing to GitHub.

## Files to modify
- `.github/workflows/android_ci.yml` (New file)
- `android/app/build.gradle.kts` (Updated for signing configurations)
- `android/key.properties` (New file, ignored by git)

## Reuse
- Existing `analysis_options.yaml` for linting.
- Existing `test/` directory for automated tests.
- Existing `pubspec.yaml` environment constraints.

## Steps
- [X] **Agent Coordination**: Initialize the agent team (DevOps, QA, Logic) using the `skills` tool. [DONE:1]
- [X] **DevOps**: Setup `.github/workflows/` directory and draft `android_ci.yml`. [DONE:2]
- [X] **DevOps/QA**: Configure local build and test scripts to mirror CI environment. [DONE:3]
- [X] **DevOps**: Update `android/app/build.gradle.kts` to handle signing secrets from environment variables. [DONE:4]
- [X] **QA**: Verify `flutter analyze` and `flutter test` pass locally. [DONE:5]
- [X] **DevOps**: Verify `flutter build apk --release` passes locally with mock/dummy signing info. [DONE:6]
- [X] **Final Review**: Submit the workflow for review. [DONE:7]

## Verification
- **Local**: Run `flutter analyze`, `flutter test`, and `flutter build apk --release` (with dummy signing) locally.
- **Remote**: Push to a branch and verify the GitHub Actions pipeline successfully completes all stages.

## Questions for the User
1. Do you have an existing Android Keystore file we should use, or should I generate a dummy one for the initial CI setup?
2. Which agent (from the AGENTS.md roles) should be the "Team Lead" for this task?
