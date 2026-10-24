pluginManagement {
    // 直接解析 KSP 发布坐标，避免部分镜像探测不存在的 marker JAR 时返回 5xx。
    resolutionStrategy {
        eachPlugin {
            if (requested.id.id == "com.google.devtools.ksp") {
                useModule("com.google.devtools.ksp:symbol-processing-gradle-plugin:${requested.version}")
            }
        }
    }
    repositories {
        val mode = providers.gradleProperty("repositoryMode").orElse("china").get()
        require(mode in setOf("china", "official")) { "repositoryMode must be china or official" }
        if (mode == "china") {
            maven("https://maven.aliyun.com/repository/google") {
                content {
                    includeGroupByRegex("com\\.android.*")
                    includeGroupByRegex("androidx.*")
                    includeGroupByRegex("com\\.google\\.android.*")
                    includeGroup("com.google.testing.platform")
                }
            }
            maven("https://maven.aliyun.com/repository/gradle-plugin")
            maven("https://maven.aliyun.com/repository/central")
        }
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        if (providers.gradleProperty("repositoryMode").orElse("china").get() == "china") {
            maven("https://maven.aliyun.com/repository/google") {
                content {
                    includeGroupByRegex("com\\.android.*")
                    includeGroupByRegex("androidx.*")
                    includeGroupByRegex("com\\.google\\.android.*")
                    includeGroup("com.google.testing.platform")
                }
            }
            maven("https://maven.aliyun.com/repository/central")
            maven("https://maven.aliyun.com/repository/public") {
                content { includeGroup("de.robv.android.xposed") }
            }
            maven("https://mirrors.cloud.tencent.com/nexus/repository/maven-public/")
        }
        google()
        mavenCentral()
        maven("https://api.xposed.info/") {
            content { includeGroup("de.robv.android.xposed") }
        }
        // 上游备用仓库：只允许 HighCapable 依赖，避免覆盖其他依赖。
        maven("https://raw.githubusercontent.com/HighCapable/maven-repository/main/repository/releases") {
            content { includeGroupByRegex("com\\.highcapable.*") }
        }
    }
}

rootProject.name = "XposedProjectTemplate"
include(":app", ":demo-app")
