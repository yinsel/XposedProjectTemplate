package com.example.xposed.demo

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val provider = GreetingProvider()
        val result = TextView(this).apply {
            textSize = 22f
            text = provider.greeting()
        }
        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            val padding = (24 * resources.displayMetrics.density).toInt()
            setPadding(padding, padding, padding, padding)
            addView(TextView(this@MainActivity).apply { setText(R.string.instructions) })
            addView(result)
            addView(Button(this@MainActivity).apply {
                setText(R.string.refresh)
                setOnClickListener { result.text = provider.greeting() }
            })
        })
    }
}
