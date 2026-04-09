# Travel Hub Mobile - Agent Roles

This document defines specialized AI agent roles for the Travel Hub Mobile project. Each role is tailored to the project's Flutter/MVVM architecture and existing conventions.

## 1. UI/Frontend Agent
**Scope:** `lib/views/`, `lib/widgets/`, `lib/l10n/`
**Responsibilities:**
- Develop and refine Flutter widgets and screen layouts.
- Ensure consistent styling and adherence to Material Design principles.
- Implement responsive UI that works across different screen sizes.
- Manage localized strings using the `intl` package and `l10n.yaml`.
**Context:** This agent should prioritize using `const` constructors and reusable components from `lib/widgets/` (e.g., `CustomTextField`).

## 2. Logic/ViewModel Agent
**Scope:** `lib/view_models/`, `lib/models/`
**Responsibilities:**
- Implement business logic and state management using the `Provider` pattern.
- Handle data transformations and input validation.
- Integrate with external APIs (using `http` or similar) and manage asynchronous operations.
- Define data structures and models for the application.
**Context:** This agent should ensure that ViewModels extend `ChangeNotifier` and properly notify listeners to update the UI.

## 3. QA/Test Agent
**Scope:** `test/`
**Responsibilities:**
- Write and maintain unit tests for ViewModels and business logic.
- Create widget tests to verify UI behavior and interactions.
- Ensure high code coverage and identify potential edge cases.
- Validate that new features do not introduce regressions.
**Context:** Tests should follow the patterns established in `test/widget_test.dart` and use `flutter_test`.

## 4. DevOps/CI-CD Agent
**Scope:** `.github/`, `pubspec.yaml`, `android/`, `ios/`
**Responsibilities:**
- Manage project dependencies and environment configurations in `pubspec.yaml`.
- Configure and maintain CI/CD workflows (e.g., GitHub Actions) for automated testing and building.
- Handle platform-specific configurations (Android/iOS) and build scripts.
- Ensure the project adheres to versioning and publication standards.
**Context:** This agent should monitor build configurations like `build.gradle` and `AndroidManifest.xml`.

## 5. Architectural Architect
**Scope:** Root directory, `analysis_options.yaml`
**Responsibilities:**
- Enforce project-wide coding standards and linting rules.
- Review overall system architecture and suggest improvements.
- Ensure cross-cutting concerns (logging, error handling) are handled consistently.
**Context:** Refer to `.github/copilot-instructions.md` for project-wide conventions and integration points.
