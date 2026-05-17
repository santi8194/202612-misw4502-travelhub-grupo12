allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    val projectPath = project.path
    if (projectPath != ":app") {
        project.evaluationDependsOn(":app")
    }

    if (project.state.executed) {
        configureAndroidNamespace(project)
    } else {
        project.afterEvaluate {
            configureAndroidNamespace(project)
        }
    }
}

fun configureAndroidNamespace(project: Project) {
    if (project.hasProperty("android")) {
        val android = project.extensions.getByName("android") as com.android.build.gradle.BaseExtension
        if (android.namespace == null) {
            val defaultNamespace = project.group.toString().replace("-", "_")
            if (project.name == "flutter_app_badger") {
                android.namespace = "fr.g123k.flutterappbadge.flutterappbadger"
            } else if (defaultNamespace.isNotEmpty()) {
                android.namespace = defaultNamespace
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
