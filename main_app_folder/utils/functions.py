import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64

def generate_pie_chart(finances):
    labels = [finance.Name for finance in finances]
    sizes = [finance.Cost for finance in finances]
    colors = plt.cm.Paired(range(len(labels)))

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)  # Explicitly close the figure after saving to memory

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

def loans_pie_chart(loans):
    labels = [loan.LenderName for loan in loans]
    sizes = [loan.LoanAmount for loan in loans]
    colors = plt.cm.Paired(range(len(labels)))

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)  # Explicitly close the figure after saving to memory

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

def create_bar_chart(data, categories):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(categories, data)
    axis.set_xticklabels(categories, rotation=22)  # Rotate x-axis labels to prevent overlap
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    return base64.b64encode(buf.getvalue()).decode('utf-8')