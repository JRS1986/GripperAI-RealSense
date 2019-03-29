#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "cameraview.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    makeOptionButton();
//    QMenu *menu = new QMenu();
//    QAction *testAction = new QAction("test menu item", this);
//    menu->addAction(testAction);
//    QToolButton* toolButton = new QToolButton();
//    toolButton->setMenu(menu);
//    ui->toolButton->setMenu(menu);


}

MainWindow::~MainWindow()
{
    delete ui;

void MainWindow::on_pushButton_clicked()
{
    cameraView = new CameraView(this);
    cameraView->show();
}

void MainWindow::on_toolButton_clicked()
{
}

void MainWindow::makeOptionButton()
{
    QMenu *menu = new QMenu();
    QAction *testAction = new QAction("Options", this);
    QToolButton* toolButton = new QToolButton();
    menu->addAction(testAction);
    ui->toolButton->setMenu(menu);
}
