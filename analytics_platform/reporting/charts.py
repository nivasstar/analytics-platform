from pathlib import Path

import matplotlib.pyplot as plt


def render_line_chart(
    dataframe,
    x,
    y,
    title,
    output_path
):
    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    chart_data = (
        dataframe[[x, y]]
        .dropna()
        .sort_values(x)
    )

    fig, ax = plt.subplots()

    ax.plot(
        chart_data[x],
        chart_data[y]
    )

    ax.set_title(title)
    ax.set_xlabel(x.replace("_", " ").title())
    ax.set_ylabel(y.replace("_", " ").title())

    fig.tight_layout()
    fig.savefig(
        path,
        dpi=150
    )

    plt.close(fig)

    return path
