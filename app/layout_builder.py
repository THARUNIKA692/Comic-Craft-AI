def build_comic_layout(
    story: list,
    image_paths: list
):

    if len(story) != len(image_paths):

        raise ValueError(
            "Story panels and image panels do not match."
        )

    layout = []

    for panel, image_path in zip(
        story,
        image_paths
    ):

        panel_data = dict(panel)

        panel_data[
            "image_path"
        ] = image_path

        layout.append(
            panel_data
        )

    return layout