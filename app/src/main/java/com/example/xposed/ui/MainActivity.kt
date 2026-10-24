package com.example.xposed.ui

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import com.example.xposed.BuildConfig
import com.example.xposed.R
import com.highcapable.yukihookapi.YukiHook

class MainActivity : Activity() {
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (24 * resources.displayMetrics.density).toInt()
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(padding, padding, padding, padding)
        }
        status = TextView(this).apply { textSize = 18f }
        content.addView(status)
        content.addView(Button(this).apply {
            setText(R.string.refresh_status)
            setOnClickListener { refreshStatus() }
        })
        setContentView(content)
    }

    override fun onResume() {
        super.onResume()
        refreshStatus()
    }

    private fun refreshStatus() {
        val active = YukiHook.Status.isModuleActive
        status.text = getString(
            R.string.module_status,
            getString(if (active) R.string.active else R.string.inactive),
            BuildConfig.VERSION_NAME,
            BuildConfig.HOOK_TARGET_PACKAGE,
            if (active) YukiHook.Status.Executor.name else getString(R.string.no_framework)
        )
    }
}
