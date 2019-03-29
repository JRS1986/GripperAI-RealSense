#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "cameraview.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void on_pushButton_clicked();

    void on_toolButton_clicked();

    void makeOptionButton();

private:
    Ui::MainWindow *ui;
    CameraView *cameraView;
};

#endif // MAINWINDOW_H
