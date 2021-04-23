import torch.nn as nn
# import torch.nn.functional as F
import torch
from torchsummary import summary

class Conv_Layer(nn.Module):
    def __init__(self,ch_in, ch_out, kernel_size, stride, padding):
        super(Conv_Layer,self).__init__()
        self.conv = nn.Conv2d(ch_in, ch_out, kernel_size=kernel_size,
                              stride=stride, padding=padding)
        self.bn = nn.BatchNorm2d(ch_out)
        self.relu = nn.ReLU()

    def forward(self,x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x

class VGG_M(nn.Module):
    def __init__(self, no_class):
        super(VGG_M,self).__init__()
        self.relu = nn.ReLU()
        self.conv1 = Conv_Layer(1, 96, kernel_size=(7, 7), stride=(2, 2), padding=(1, 1))
        self.maxpool1 = nn.MaxPool2d(kernel_size=(3,3), stride=(2,2))
        self.conv2 = Conv_Layer(96, 256, kernel_size=(5, 5), stride=(2, 2), padding=(1, 1))
        self.maxpool2 = nn.MaxPool2d(kernel_size=(3, 3), stride=(2, 2))
        self.conv3 = Conv_Layer(256, 384, kernel_size=(3, 3), stride=(1, 1),padding=(1, 1))
        self.conv4 = Conv_Layer(384, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv5 = Conv_Layer(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.maxpool5 = nn.MaxPool2d(kernel_size=(5, 3), stride=(3, 2))
        self.fc6 = Conv_Layer(256, 4096, kernel_size=(9, 1), stride=(1, 1), padding=0)
        self.apool6 = nn.AdaptiveAvgPool2d((1,1))
        self.fc7 = nn.Linear(4096,1024)
        self.fc8 = nn.Linear(1024, no_class)

    def features(self,x):
        out = self.conv1(x)
        out = self.maxpool1(out)
        out = self.conv2(out)
        out = self.maxpool2(out)
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.conv5(out)
        out = self.maxpool5(out)
        out = self.fc6(out)
        out = self.apool6(out)
        out = out.view(out.size(0), -1)
        return out

    def classifier(self,x):
        out = self.fc7(x)
        out = self.relu(out)
        out = self.fc8(out)
        return out

    def forward(self,x):
        out = self.features(x)
        out = self.classifier(out)
        return out

class DCASE_PAST(nn.Module):
    def __init__(self, no_class):
        super(DCASE_PAST,self).__init__()
        self.conv1 = Conv_Layer(1, 64, kernel_size=(8,2), stride=(1,1), padding=0)
        self.maxpool1 = nn.MaxPool2d(kernel_size=(1,3), stride=(1,3))
        self.conv2 = Conv_Layer(64, 128, kernel_size=(1,8), stride=(1,1), padding=0)
        self.maxpool2 = nn.MaxPool2d(kernel_size=(1,4), stride=(1,4))
        self.conv3 = Conv_Layer(128, 256, kernel_size=(1,10), stride=(1,1), padding=0)
        self.conv4 = Conv_Layer(256, 512, kernel_size=(10,1), stride=(1,1), padding=0)
        self.apool4 = nn.AdaptiveAvgPool2d((1,1))
        self.fc5 = nn.Linear(512, 256)
        self.drop5 = nn.Dropout2d()
        self.fc6 = nn.Linear(256, no_class)

    def forward(self, x):
        out = self.conv1(x)
        out = self.maxpool1(out)
        out = self.conv2(out)
        out = self.maxpool2(out)
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.apool4(out)
        out = out.view(out.size(0), -1)
        out = self.fc5(out)
        out = self.drop5(out)
        out = self.fc6(out)
        return out

class DCASE_PAST2(nn.Module):
    def __init__(self, no_class):
        super(DCASE_PAST2,self).__init__()
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=(2,2), stride=(2,2))
        self.conv1 = Conv_Layer(1, 64, kernel_size=(3,3), stride=(1,1), padding=0)
        self.conv2 = Conv_Layer(64, 128, kernel_size=(3,3), stride=(1,1), padding=0)
        self.conv3 = Conv_Layer(128, 256, kernel_size=(3,3), stride=(1,1), padding=0)
        self.conv4 = Conv_Layer(256, 512, kernel_size=(3,3), stride=(1,1), padding=0)
        self.conv5 = Conv_Layer(512, 512, kernel_size=(3,3), stride=(1,1), padding=0)
        self.glbmaxpool = nn.AdaptiveMaxPool2d((1,1))
        self.fc6 = nn.Linear(512, 256)
        self.fc7 = nn.Linear(256, no_class)

    def forward(self, x):
        out = self.conv1(x)
        out = self.maxpool(out)
        out = self.conv2(out)
        out = self.maxpool(out)
        out = self.conv3(out)
        out = self.maxpool(out)
        out = self.conv4(out)
        out = self.conv5(out)
        out = self.glbmaxpool(out)
        out = out.view(out.size(0), -1)
        out = self.fc6(out)
        out = self.relu(out)
        out = self.fc7(out)
        return out
    
if __name__=="__main__":
    from torchsummary import summary
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model=VGG_M(5)
    model.to(device)
    print(summary(model, (1,128,313)))