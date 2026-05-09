// OMNI Framework Qt5/Qt6 Desktop GUI
#include <QApplication>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>
#include <QLabel>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QWidget window;
    window.setWindowTitle("OMNI Qt Console");
    window.resize(300, 150);

    QVBoxLayout *layout = new QVBoxLayout(&window);

    QLabel *label = new QLabel("OMNI Sub-Agent Status: Idle");
    layout->addWidget(label);

    QPushButton *button = new QPushButton("Initialize Compute Engine");
    QObject::connect(button, &QPushButton::clicked, [label]() {
        label->setText("OMNI Sub-Agent Status: Running...");
    });
    
    layout->addWidget(button);
    window.show();

    return app.exec();
}
