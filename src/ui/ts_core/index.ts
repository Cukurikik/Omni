// ===========================================================================
// OMNI UI LAYER — TypeScript Core Barrel Export
// ===========================================================================
// Auto-generated barrel export for all 49 OMNI Interface engines.
// This file provides a single entry point for consuming all UI/TS engines.
// ===========================================================================

/**
 * OMNI Interface Layer — Central TypeScript Package.
 *
 * This package contains 49+ production-grade interface engines spanning:
 *   - ML Curriculum & Knowledge Graphs
 *   - Audio/Visual Web Components
 *   - Data Science Resource Navigators
 *   - Computer Vision Recipe Engines
 *   - Web ML Inference (TensorFlow.js, ml5.js)
 *
 * All engines follow OMNI Blueprint standards:
 *   - Strong TypeScript typing
 *   - evaluateHealth() for observability
 *   - No direct imports from system/compute layers (use @omni-bridge)
 */

export { OmniAcademicRoadmapEngine } from "./omni_academic_roadmap_engine";
export { OmniAICareerRoadmapEngine } from "./omni_ai_career_roadmap_engine";
export { OmniAiCheatsheetsEngine } from "./omni_ai_cheatsheets_engine";
export { OmniAIFoundationalEngine } from "./omni_ai_foundational_engine";
export { OmniAiLearningCurriculumEngine } from "./omni_ai_learning_curriculum_engine";
export { OmniAIProjectNavigatorEngine } from "./omni_ai_project_navigator_engine";
export { OmniAudioMixerEngine } from "./omni_audio_mixer_engine";
export { OmniAudioWallpaperEngine } from "./omni_audio_wallpaper_engine";
export { OmniAutonomousSleepResearchEngine } from "./omni_autonomous_sleep_research_engine";
export { OmniAwesomePytorchListEngine } from "./omni_awesome_pytorch_list_engine";
export { OmniSynthVoice as OmniAwesomeWebaudioEngine } from "./omni_awesome_webaudio_engine";
export { OmniChartRendererEngine } from "./omni_chart_renderer_engine";
export { OmniComputerVisionRecipesEngine } from "./omni_computer_vision_recipes_engine";
export { OmniCvprSotaAggregationEngine } from "./omni_cvpr_sota_aggregation_engine";
export { OmniDatasciResourceEngine } from "./omni_datasci_resource_engine";
export { OmniDeepLearningResourceEngine } from "./omni_deep_learning_resource_engine";
export { OmniDynamicAudioEngine } from "./omni_dynamic_audio_engine";
export { OmniFormValidatorEngine } from "./omni_form_validator_engine";
export { OmniGridsoundEngine } from "./omni_gridsound_engine";
export { OmniJammerEngine } from "./omni_jammer_engine";
export { OmniMediaPlayerEngine } from "./omni_media_player_engine";
export { OmniMl5jsWebCapabilitiesEngine } from "./omni_ml5js_web_capabilities_engine";
export { OmniMl100DaysCurriculumEngine } from "./omni_ml_100_days_curriculum_engine";
export { OmniMlCourseFundamentalsEngine } from "./omni_ml_course_fundamentals_engine";
export { OmniMLCurriculumEngine } from "./omni_ml_curriculum_engine";
export { OmniMlNlpCurriculumEngine } from "./omni_ml_nlp_curriculum_engine";
export { OmniMlPythonCatalogEngine } from "./omni_ml_python_catalog_engine";
export { OmniModelscopeMaasOrchestratorEngine } from "./omni_modelscope_maas_orchestrator_engine";
export { OmniNetronGraphEngine } from "./omni_netron_graph_engine";
export { OmniNumericalLinearAlgebraEngine } from "./omni_numerical_linear_algebra_engine";
export { OmniObjectDetectionTimelineEngine } from "./omni_object_detection_timeline_engine";
export { OmniOpticalCharacterEngine } from "./omni_optical_character_engine";
export { OmniOxfordDeepNlpEngine } from "./omni_oxford_deep_nlp_engine";
export { OmniPizzicatoEngine } from "./omni_pizzicato_engine";
export { OmniPracticalMlPatternsEngine } from "./omni_practical_ml_patterns_engine";
export { OmniPromptRoutingEngine } from "./omni_prompt_routing_engine";
export { OmniPythonLearningParkEngine } from "./omni_python_learning_park_engine";
export { OmniPytorchDeepLearningCurriculumEngine } from "./omni_pytorch_deep_learning_curriculum_engine";
export { OmniQixMlKnowledgeEngine as OmniQixMachineLearningKnowledgeEngine } from "./omni_qix_machine_learning_knowledge_engine";
export { OmniReactiveUiEngine } from "./omni_reactive_ui_engine";
export { OmniStateMachineEngine } from "./omni_state_machine_engine";
export { OmniTensorflowCourseEngine } from "./omni_tensorflow_course_engine";
export { OmniTfjsWebglInferenceEngine } from "./omni_tfjs_webgl_inference_engine";
export { OmniTinymlCurriculumEngine } from "./omni_tinyml_curriculum_engine";
export { OmniTransferLearningKnowledgeEngine } from "./omni_transfer_learning_knowledge_engine";
export { OmniTunaEngine } from "./omni_tuna_engine";
export { OmniMediaRecorderSimulator as OmniVideojsRecordEngine } from "./omni_videojs_record_engine";
export { OmniVirtualListEngine } from "./omni_virtual_list_engine";
export { OmniWaveformVisualizerEngine } from "./omni_waveform_visualizer_engine";
export { OmniAgentChatUIEngine } from "./omni_agent_chat_ui_engine";

/**
 * Returns a summary of all available UI engines.
 */
export function getUiEngineManifest(): { total: number; layer: string; engines: string[] } {
    return {
        total: 50,
        layer: "ui/ts_core",
        engines: [
            "OmniAcademicRoadmapEngine", "OmniAICareerRoadmapEngine", "OmniAiCheatsheetsEngine",
            "OmniAIFoundationalEngine", "OmniAiLearningCurriculumEngine", "OmniAIProjectNavigatorEngine",
            "OmniAgentChatUIEngine",
            "OmniAudioMixerEngine", "OmniAudioWallpaperEngine", "OmniAutonomousSleepResearchEngine",
            "OmniAwesomePytorchListEngine", "OmniAwesomeWebaudioEngine", "OmniChartRendererEngine",
            "OmniComputerVisionRecipesEngine", "OmniCvprSotaAggregationEngine", "OmniDatasciResourceEngine",
            "OmniDeepLearningResourceEngine", "OmniDynamicAudioEngine", "OmniFormValidatorEngine",
            "OmniGridsoundEngine", "OmniJammerEngine", "OmniMediaPlayerEngine",
            "OmniMl5jsWebCapabilitiesEngine", "OmniMl100DaysCurriculumEngine", "OmniMlCourseFundamentalsEngine",
            "OmniMLCurriculumEngine", "OmniMlNlpCurriculumEngine", "OmniMlPythonCatalogEngine",
            "OmniModelscopeMaasOrchestratorEngine", "OmniNetronGraphEngine", "OmniNumericalLinearAlgebraEngine",
            "OmniObjectDetectionTimelineEngine", "OmniOpticalCharacterEngine", "OmniOxfordDeepNlpEngine",
            "OmniPizzicatoEngine", "OmniPracticalMlPatternsEngine", "OmniPromptRoutingEngine",
            "OmniPythonLearningParkEngine", "OmniPytorchDeepLearningCurriculumEngine",
            "OmniQixMachineLearningKnowledgeEngine", "OmniReactiveUiEngine", "OmniStateMachineEngine",
            "OmniTensorflowCourseEngine", "OmniTfjsWebglInferenceEngine", "OmniTinymlCurriculumEngine",
            "OmniTransferLearningKnowledgeEngine", "OmniTunaEngine", "OmniVideojsRecordEngine",
            "OmniVirtualListEngine", "OmniWaveformVisualizerEngine",
        ],
    };
}
