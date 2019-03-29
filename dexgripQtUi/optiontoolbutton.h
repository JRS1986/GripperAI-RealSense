#ifndef OPTIONTOOLBUTTON_H
#define OPTIONTOOLBUTTON_H

#include <QToolButton>
#include <QDebug>

class OptionToolButton : public QToolButton
{
    Q_OBJECT
public:
    explicit OptionToolButton(QWidget *parent = 0);
};

#endif // OPTIONTOOLBUTTON_H
