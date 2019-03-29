#ifndef CAMERAVIEW_H
#define CAMERAVIEW_H

#include <QDialog>

namespace Ui {
class CameraView;
}

class CameraView : public QDialog
{
    Q_OBJECT

public:
    explicit CameraView(QWidget *parent = 0);
    ~CameraView();

private:
    Ui::CameraView *ui;
};

#endif // CAMERAVIEW_H
