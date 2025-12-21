pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        // --- זה החלק שהיה חסר לך ---
        maven { url = uri("https://chaquo.com/maven") }
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        // --- וגם כאן צריך את זה ---
        maven { url = uri("https://chaquo.com/maven") }
    }
}

rootProject.name = "HalachaWatch"
include(":app")