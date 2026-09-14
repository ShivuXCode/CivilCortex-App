from metadata_schema import ImageMetadata, DefectInstance, CalibrationData
from split_generator import get_grouping_key

def test_metadata_hierarchy():
    # Test that a valid image metadata respects the hierarchy
    defect = DefectInstance(
        defect_instance_id="d1",
        defect_type="crack",
        morphology_labels=["diagonal", "branching"],
        polygon=[[0,0], [10,10], [0,10]],
        bounding_box=[0, 0, 10, 10]
    )
    
    metadata = ImageMetadata(
        image_id="img1",
        source_id="src1",
        building_id="bld1",
        inspection_id="insp1",
        image_width=1000,
        image_height=1000,
        calibration=CalibrationData(is_calibrated=False),
        defects=[defect]
    )
    
    assert metadata.building_id == "bld1"
    # One defect instance, multiple morphology tags (semantic validation)
    assert len(metadata.defects) == 1
    assert "diagonal" in metadata.defects[0].morphology_labels
    
def test_grouping_key_leakage_prevention():
    # Test hierarchical grouping key
    img_with_building = ImageMetadata(
        image_id="img1", source_id="src1", building_id="bld1", image_width=100, image_height=100
    )
    assert get_grouping_key(img_with_building) == "bld_bld1"
    
    img_with_inspection = ImageMetadata(
        image_id="img2", source_id="src1", inspection_id="insp1", image_width=100, image_height=100
    )
    assert get_grouping_key(img_with_inspection) == "insp_insp1"
    
    img_with_defect = ImageMetadata(
        image_id="img3", source_id="src1", image_width=100, image_height=100,
        defects=[DefectInstance(
            defect_instance_id="d1", defect_type="crack", polygon=[[0,0], [1,1], [0,1]], bounding_box=[0,0,1,1]
        )]
    )
    assert get_grouping_key(img_with_defect) == "def_d1"
    
    img_isolated = ImageMetadata(
        image_id="img4", source_id="src1", image_width=100, image_height=100
    )
    assert get_grouping_key(img_isolated) == "img_img4"
