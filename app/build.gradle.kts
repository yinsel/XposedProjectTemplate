import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.ksp)
}

val template = Properties().apply {
    rootProject.file("template.properties").reader(Charsets.UTF_8).use { load(it) }
}
fun templateValue(key: String) = requireNotNull(template.getProperty(key)) { "Missing $key" }
fun quoted(value: String) = "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\""
val storePath = providers.environmentVariable("RELEASE_STORE_FILE").orNull
val signingValues = listOf("RELEASE_STORE_PASSWORD", "RELEASE_KEY_ALIAS", "RELEASE_KEY_PASSWORD")
val signingRequested = storePath != null || signingValues.any { providers.environmentVariable(it).isPresent }
val releaseSigningReady = !storePath.isNullOrBlank() && signingValues.all {
    !providers.environmentVariable(it).orNull.isNullOrBlank()
}
require(!signingRequested || releaseSigningReady) { "Release signing requires all four RELEASE_* variables" }

android {
    namespace = "com.example.xposed"
    compileSdk = 37

    defaultConfig {
        applicationId = templateValue("module.applicationId")
        minSdk = 26
        targetSdk = 37
        versionCode = templateValue("module.versionCode").toInt()
        versionName = templateValue("module.versionName")
        resValue("string", "app_name", templateValue("module.name"))
        resValue("string", "module_description", templateValue("module.description"))
        resValue("string", "hook_target_package", templateValue("hook.targetPackage"))
        buildConfigField("String", "HOOK_TARGET_PACKAGE", quoted(templateValue("hook.targetPackage")))
        buildConfigField("String", "HOOK_TARGET_CLASS", quoted(templateValue("hook.targetClass")))
        buildConfigField("String", "HOOK_TARGET_METHOD", quoted(templateValue("hook.targetMethod")))
    }
    signingConfigs {
        if (releaseSigningReady) {
            create("release") {
                storeFile = rootProject.file(storePath!!)
                storePassword = providers.environmentVariable("RELEASE_STORE_PASSWORD").get()
                keyAlias = providers.environmentVariable("RELEASE_KEY_ALIAS").get()
                keyPassword = providers.environmentVariable("RELEASE_KEY_PASSWORD").get()
            }
        }
    }
    buildTypes {
        release {
            // 模板优先保证反射与生成入口稳定；启用 R8 前请自行补充规则和设备回归。
            isMinifyEnabled = false
            if (releaseSigningReady) signingConfig = signingConfigs.getByName("release")
        }
    }
    buildFeatures { buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    lint { abortOnError = true }
}

dependencies {
    implementation(platform(libs.yukihook.bom))
    implementation(libs.yukihook.core)
    implementation(libs.yukihook.runtime.xposed82)
    implementation(libs.yukihook.extension.kavaref)
    ksp(libs.yukihook.compiler)
    compileOnly(libs.xposed.api)
    implementation(platform(libs.kavaref.bom))
    implementation(libs.kavaref.core)
    implementation(libs.kavaref.extension)
}
