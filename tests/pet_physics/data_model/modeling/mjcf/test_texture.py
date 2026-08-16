from pet_physics.data_model.modeling.mjcf.texture import Texture


def test_texture_to_xml_string():
    texture = Texture(
        name="grid",
        type="2d",
        builtin="checker",
        rgb1=(0.1, 0.2, 0.3),
        rgb2=(0.2, 0.3, 0.4),
        width=300,
        height=300,
        mark="edge",
        markrgb=(0.2, 0.3, 0.4),
    )

    expected_xml_string = """<texture name="grid" type="2d" builtin="checker" width="300" height="300" rgb1="0.1 0.2 0.3" rgb2="0.2 0.3 0.4" mark="edge" markrgb="0.2 0.3 0.4" />"""

    assert texture.to_xml_string() == expected_xml_string
