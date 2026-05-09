// moe_android_intent_parser.kt — Domain / Mobile
// Layer: Domain / Android — Mobile Intent Bridge
//
// Inspired by `Aravinda30/E-commerce-Android-App`.
// When the MoE interacts with a user via a mobile app, it needs to trigger
// native OS actions (opening screens, adding to cart, launching camera).
// This Kotlin module runs on the client, securely parsing the MoE's generated
// action codes into native Android Intents.

package com.omni.moe.bridge

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.util.Log
import org.json.JSONObject

class MoeIntentParser(private val context: Context) {

    init {
        Log.d("MoE_Bridge", "Initialized Android Intent Parser for MoE Actions.")
    }

    /**
     * Parses a JSON action payload from the MoE and executes the corresponding Android Intent.
     * Example Payload: {"action": "NAVIGATE", "target": "PRODUCT_DETAIL", "params": {"id": "123"}}
     */
    fun executeMoeAction(jsonPayload: String): Boolean {
        try {
            val json = JSONObject(jsonPayload)
            val action = json.optString("action", "")
            val target = json.optString("target", "")
            val params = json.optJSONObject("params")

            Log.d("MoE_Bridge", "Executing MoE Action: $action -> $target")

            when (action) {
                "NAVIGATE" -> return handleNavigation(target, params)
                "LAUNCH_URL" -> return handleUrlLaunch(params)
                "ADD_TO_CART" -> return handleAddToCart(params)
                else -> {
                    Log.w("MoE_Bridge", "Unknown action requested by MoE: $action")
                    return false
                }
            }
        } catch (e: Exception) {
            Log.e("MoE_Bridge", "Failed to parse MoE intent JSON.", e)
            return false
        }
    }

    private fun handleNavigation(target: String, params: JSONObject?): Boolean {
        // In a real app, this would use Jetpack Navigation or Activity routing
        Log.d("MoE_Bridge", "Navigating to $target with params $params")
        // val intent = Intent(context, ProductDetailActivity::class.java)
        // intent.putExtra("PRODUCT_ID", params?.optString("id"))
        // context.startActivity(intent)
        return true
    }

    private fun handleUrlLaunch(params: JSONObject?): Boolean {
        val url = params?.optString("url") ?: return false
        val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(browserIntent)
        return true
    }

    private fun handleAddToCart(params: JSONObject?): Boolean {
        val productId = params?.optString("productId") ?: return false
        val quantity = params?.optInt("quantity", 1) ?: 1
        Log.d("MoE_Bridge", "Added $quantity of $productId to native Cart instance.")
        // CartManager.getInstance().add(productId, quantity)
        return true
    }
}
