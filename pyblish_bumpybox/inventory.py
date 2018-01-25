from pyblish import api


# ----Collection
plugins_copy_to_clipboard_action_Report = api.CollectorOrder - 1
plugins_collect_source_CollectScene = api.CollectorOrder + 0.1
plugins_collect_scene_version_CollectSceneVersion = api.CollectorOrder + 0.1
plugins_collect_existing_files_CollectExistingFiles = api.CollectorOrder + 0.25
plugins_collect_reviews_CollectReviews = api.CollectorOrder + 0.3
plugins_collect_sorting_CollectSorting = api.CollectorOrder + 0.49

# ----Validation
plugins_persist_publish_state_PersistPublishState = api.ValidatorOrder

# ----Extraction
plugins_extract_review_ExtractReview = api.ExtractorOrder
plugins_extract_review_ExtractReviewTranscode = api.ExtractorOrder + 0.02
plugins_extract_review_ExtractReviewTranscodeNukeStudio = (
    api.ExtractorOrder + 0.02
)
plugins_extract_json_ExtractJSON = api.ExtractorOrder + 1

# AfterEffects
aftereffects_collect_render_items_CollectRenderItems = api.CollectorOrder
aftereffects_collect_scene_CollectScene = api.CollectorOrder

aftereffects_validate_output_path_ValidateOutputPath = api.ValidatorOrder
aftereffects_validate_scene_path_ValidateScenePath = api.ValidatorOrder
aftereffects_validate_unique_comp_renders_ValidateUniqueCompRenders = (
    api.ValidatorOrder
)

aftereffects_append_deadline_data_AppendDeadlineData = api.ExtractorOrder
aftereffects_append_ftrack_audio_AppendFtrackAudio = api.ExtractorOrder
aftereffects_extract_local_ExtractLocal = api.ExtractorOrder

celaction_collect_scene_CollectScene = api.CollectorOrder
celaction_collect_render_CollectRender = api.CollectorOrder + 0.1

celaction_extract_deadline_ExtractDeadline = api.ExtractorOrder
celaction_extract_render_images_ExtractRenderImages = api.ExtractorOrder
celaction_extract_render_images_ExtractRenderMovie = api.ExtractorOrder + 0.1
celaction_extract_deadline_movie_ExtractDeadlineMovie = (
    api.ExtractorOrder + 0.4
)

# Deadline
deadline_OnJobFinished_collect_output_CollectOutput = api.CollectorOrder
deadline_OnJobSubmitted_collect_movie_CollectMovie = api.CollectorOrder
deadline_OnJobSubmitted_collect_render_CollectRender = api.CollectorOrder
deadline_collect_houdini_parameters_CollectHoudiniParameters = (
    api.CollectorOrder + 0.1
)
deadline_collect_maya_parameters_CollectMayaParameters = (
    api.CollectorOrder + 0.1
)
deadline_collect_nuke_parameters_CollectNukeParameters = (
    api.CollectorOrder + 0.2
)
deadline_collect_houdini_render_CollectHoudiniRender = api.CollectorOrder + 0.4
deadline_collect_family_CollectFamily = api.CollectorOrder + 0.4

deadline_validate_houdini_parameters_ValidateHoudiniParameters = (
    api.ValidatorOrder
)
deadline_validate_maya_parameters_ValidateMayaParameters = api.ValidatorOrder
deadline_validate_nuke_parameters_ValidateNukeParameters = api.ValidatorOrder

deadline_extract_ftrack_path_ExtractFtrackPath = api.ExtractorOrder
deadline_extract_houdini_ExtractHoudini = api.ExtractorOrder
deadline_extract_job_name_ExtractJobName = api.ExtractorOrder
deadline_extract_maya_ExtractMaya = api.ExtractorOrder
deadline_extract_nuke_ExtractNuke = api.ExtractorOrder
deadline_extract_suspended_ExtractSuspended = api.ExtractorOrder

deadline_integrate_collection_IntegrateCollection = api.IntegratorOrder - 0.1

# Ftrack
ftrack_collect_nukestudio_CollectNukeStudioEntities = api.CollectorOrder + 0.1
ftrack_collect_nukestudio_CollectNukeStudioProjectData = (
    api.CollectorOrder + 0.1
)
ftrack_collect_version_CollectVersion = api.CollectorOrder + 0.2
ftrack_collect_family_CollectFamily = api.CollectorOrder + 0.4

ftrack_validate_assets_ValidateAssets = api.ValidatorOrder
ftrack_validate_nuke_settings_ValidateNukeSettings = api.ValidatorOrder
ftrack_validate_nukestudio_ValidateNukeStudioProjectData = api.ValidatorOrder
ftrack_validate_nukestudio_tasks_ValidateNukeStudioTasks = api.ValidatorOrder

ftrack_extract_components_ExtractCache = api.ExtractorOrder
ftrack_extract_components_ExtractCamera = api.ExtractorOrder
ftrack_extract_components_ExtractGeometry = api.ExtractorOrder
ftrack_extract_components_ExtractGizmo = api.ExtractorOrder
ftrack_extract_components_ExtractImg = api.ExtractorOrder
ftrack_extract_components_ExtractLUT = api.ExtractorOrder
ftrack_extract_components_ExtractMovie = api.ExtractorOrder
ftrack_extract_components_ExtractScene = api.ExtractorOrder
ftrack_extract_entities_ExtractProject = api.ExtractorOrder
ftrack_extract_nukestudio_ExtractThumbnail = api.ExtractorOrder
ftrack_extract_entities_ExtractEpisode = api.ExtractorOrder + 0.01
ftrack_extract_entities_ExtractSequence = api.ExtractorOrder + 0.02
ftrack_extract_entities_ExtractShot = api.ExtractorOrder + 0.03
ftrack_extract_entities_ExtractLinkAssetbuilds = api.ExtractorOrder + 0.03
ftrack_extract_entities_ExtractTasks = api.ExtractorOrder + 0.04
ftrack_extract_entities_ExtractCommit = api.ExtractorOrder + 0.05
ftrack_extract_entities_ExtractNukeStudio = api.ExtractorOrder + 0.05
ftrack_extract_thumbnail_ExtractThumbnailImg = api.ExtractorOrder + 0.1
ftrack_extract_review_ExtractReview = api.ExtractorOrder + 0.2
ftrack_extract_components_ExtractComponents = api.ExtractorOrder + 0.4
ftrack_other_link_source_OtherLinkSource = api.ExtractorOrder + 1

ftrack_integrate_status_IntegrateStatus = api.IntegratorOrder

# Hiero
hiero_collect_items_CollectItems = api.CollectorOrder

hiero_validate_names_ValidateNames = api.ValidatorOrder

hiero_extract_transcode_BumpyboxExtractTranscodeH264 = api.ExtractorOrder - 0.1
hiero_extract_transcode_BumpyboxExtractTranscodeJPEG = api.ExtractorOrder - 0.1
hiero_extract_audio_ExtractAudio = api.ExtractorOrder
hiero_extract_ftrack_shot_ExtractFtrackShot = api.ExtractorOrder
hiero_extract_nuke_script_ExtractNukeScript = api.ExtractorOrder
hiero_extract_transcode_ExtractTranscode = api.ExtractorOrder
hiero_extract_ftrack_components_ExtractFtrackComponents = (
    api.ExtractorOrder + 0.1
)
hiero_extract_ftrack_tasks_ExtractFtrackTasks = api.ExtractorOrder + 0.1
hiero_extract_ftrack_thumbnail_ExtractFtrackThumbnail = (
    api.ExtractorOrder + 0.1
)

# Houdini
houdini_collect_Collect = api.CollectorOrder

houdini_validate_alembic_ValidateAlembic = api.ValidatorOrder
houdini_validate_dynamics_ValidateDynamics = api.ValidatorOrder
houdini_validate_geometry_ValidateGeometry = api.ValidatorOrder
houdini_validate_mantra_camera_ValidateMantraCamera = api.ValidatorOrder
houdini_validate_mantra_settings_ValidateMantraSettings = api.ValidatorOrder
houdini_validate_output_path_ValidateOutputPath = api.ValidatorOrder

houdini_extract_scene_save_ExtractSceneSave = api.ExtractorOrder - 0.1
houdini_extract_local_ExtractLocal = api.ExtractorOrder

# Maya
maya_collect_framerate_CollectFramerate = api.CollectorOrder - 0.5
maya_collect_files_CollectFiles = api.CollectorOrder
maya_collect_playblasts_CollectPlayblasts = api.CollectorOrder
maya_collect_render_layers_CollectRenderlayers = api.CollectorOrder
maya_collect_sets_CollectSets = api.CollectorOrder
maya_collect_playblasts_CollectPlayblastsProcess = api.CollectorOrder + 0.01
maya_collect_playblasts_CollectPlayblastsPublish = api.CollectorOrder + 0.01
maya_collect_sets_CollectSetsLocal = api.CollectorOrder + 0.01

maya_validate_display_layer_ValidateDisplayLayer = api.ValidatorOrder
maya_validate_hierarchy_ValidateHierarchy = api.ValidatorOrder
maya_validate_intermediate_shapes_ValidateIntermediateShapes = (
    api.ValidatorOrder
)
maya_validate_points_ValidatePoints = api.ValidatorOrder
maya_validate_shape_name_ValidateShapeName = api.ValidatorOrder
maya_validate_smooth_display_ValidateSmoothDisplay = api.ValidatorOrder
maya_validate_transforms_ValidateTransforms = api.ValidatorOrder
maya_validate_arnold_setings_ValidateArnoldSettings = api.ValidatorOrder
maya_validate_file_path_ValidateFilePath = api.ValidatorOrder
maya_validate_render_camera_ValidateRenderCamera = api.ValidatorOrder
maya_validate_render_layer_settings_ValidateRenderLayerSettings = (
    api.ValidatorOrder
)
maya_validate_vray_settings_ValidateVraySettings = api.ValidatorOrder

maya_extract_construction_history_ExtractConstructionHistory = (
    api.ExtractorOrder - 0.1
)
maya_rigging_extract_disconnect_animation_ExtractDisconnectAnimation = (
    api.ExtractorOrder - 0.1
)
maya_validate_scene_modified_ValidateSceneModified = api.ExtractorOrder - 0.49
maya_extract_alembic_ExtractAlembic = api.ExtractorOrder
maya_extract_formats_ExtractFormats = api.ExtractorOrder
maya_extract_playblast_ExtractPlayblast = api.ExtractorOrder
maya_extract_render_layer_ExtractRenderLayer = api.ExtractorOrder

# Nuke
nuke_collect_selection_CollectSelection = api.CollectorOrder - 0.1
nuke_collect_backdrops_CollectBackdrops = api.CollectorOrder + 0.1
nuke_collect_framerate_CollectFramerate = api.CollectorOrder
nuke_collect_reads_CollectReads = api.CollectorOrder
nuke_collect_write_geo_CollectWriteGeo = api.CollectorOrder
nuke_collect_writes_CollectWrites = api.CollectorOrder
nuke_collect_write_geo_CollectCacheProcess = api.CollectorOrder + 0.01
nuke_collect_write_geo_CollectCachePublish = api.CollectorOrder + 0.01
nuke_collect_writes_CollectWritesProcess = api.CollectorOrder + 0.01
nuke_collect_writes_CollectWritesPublish = api.CollectorOrder + 0.01
nuke_collect_groups_CollectGroups = api.CollectorOrder + 0.1

nuke_validate_datatype_ValidateDatatype = api.ValidatorOrder
nuke_validate_frame_rate_ValidateFrameRate = api.ValidatorOrder
nuke_validate_group_node_ValidateGroupNode = api.ValidatorOrder
nuke_validate_proxy_mode_ValidateProxyMode = api.ValidatorOrder
nuke_validate_read_node_ValidateReadNode = api.ValidatorOrder
nuke_validate_write_node_ValidateWriteNode = api.ValidatorOrder
nuke_validate_writegeo_node_ValidateWriteGeoNode = api.ValidatorOrder

nuke_extract_scene_save_ExtractSceneSave = api.ExtractorOrder - 0.49
nuke_extract_output_directory_ExtractOutputDirectory = api.ExtractorOrder - 0.1
nuke_extract_backdrop_ExtractBackdrop = api.ExtractorOrder
nuke_extract_group_ExtractGroup = api.ExtractorOrder
nuke_extract_write_Extract = api.ExtractorOrder
nuke_extract_write_ExtractCache = api.ExtractorOrder
nuke_extract_write_ExtractCamera = api.ExtractorOrder
nuke_extract_write_ExtractGeometry = api.ExtractorOrder
nuke_extract_write_ExtractWrite = api.ExtractorOrder
nuke_extract_review_ExtractReview = api.ExtractorOrder + 0.01

# NukeStudio
nukestudio_collect_CollectFramerate = api.CollectorOrder
nukestudio_collect_CollectTrackItems = api.CollectorOrder
nukestudio_collect_CollectTasks = api.CollectorOrder + 0.01

nukestudio_validate_names_ValidateNames = api.ValidatorOrder
nukestudio_validate_names_ValidateNamesFtrack = api.ValidatorOrder
nukestudio_validate_projectroot_ValidateProjectRoot = api.ValidatorOrder
nukestudio_validate_resolved_paths_ValidateResolvedPaths = api.ValidatorOrder
nukestudio_validate_task_ValidateImageSequence = api.ValidatorOrder
nukestudio_validate_task_ValidateOutputRange = api.ValidatorOrder
nukestudio_validate_track_item_ValidateTrackItem = api.ValidatorOrder
nukestudio_validate_track_item_ValidateTrackItemFtrack = api.ValidatorOrder
nukestudio_validate_viewer_lut_ValidateViewerLut = api.ValidatorOrder

nukestudio_extract_review_ExtractReview = api.ExtractorOrder
nukestudio_extract_tasks_ExtractTasks = api.ExtractorOrder

# RoyalRender
royalrender_collect_CollectMayaSets = api.CollectorOrder + 0.1
royalrender_collect_CollectNukeWrites = api.CollectorOrder + 0.1

royalrender_extract_maya_ExtractMaya = api.ExtractorOrder
royalrender_extract_maya_alembic_ExtractMovie = api.ExtractorOrder
royalrender_extract_nuke_ExtractNuke = api.ExtractorOrder

# TVPaint
tvpaint_extract_deadline_ExtractDeadline = api.ExtractorOrder - 0.1
tvpaint_collect_scene_arg_CollectSceneArg = api.CollectorOrder - 0.05
tvpaint_collect_render_CollectRender = api.CollectorOrder + 0.1

tvpaint_validate_scene_path_ValidateScenePath = api.ValidatorOrder

tvpaint_extract_hobsoft_scene_ExtractHobsoftScene = api.ExtractorOrder


def get_order(module, name):
    print module
    print name
    return api.ExtractorOrder
