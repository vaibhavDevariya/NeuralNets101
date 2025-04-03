import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor

transform = transforms.Compose(
    [ToTensor(),
     transforms.Normalize((0.5,),(0.5,))]
)

training_data = datasets.FashionMNIST(root="data",download=True,train=True,transform=transform)
testing_data = datasets.FashionMNIST(root="data",download=True,train=False,transform=transform)

training_dataloader = DataLoader(training_data,batch_size=64,shuffle=True)
testing_dataloader = DataLoader(testing_data,batch_size=64,shuffle=True)

class CNN(nn.Module):
  def __init__(self):
    super().__init__()
    self.conv1 = nn.Conv2d(1,6,5)
    self.pool = nn.MaxPool2d(2,2)
    self.conv2 = nn.Conv2d(6,16,5)
    self.fc1 = nn.Linear(16*4*4, 120)
    self.fc2 = nn.Linear(120,84)
    self.fc3 = nn.Linear(84,10)

  def forward(self,x):
    x = self.pool(nn.functional.relu(self.conv1(x)))
    x = self.pool(nn.functional.relu(self.conv2(x)))
    x = torch.flatten(x,1)
    x = nn.functional.relu(self.fc1(x))
    x = nn.functional.relu(self.fc2(x))
    x = self.fc3(x)
    return x

model = CNN()

loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.SGD(model.parameters(),lr=1e-3)


def train(dataloader, model, loss_fn, optimizer):
  size = len(dataloader.dataset)
  model.train()
  for batch, (x,y) in enumerate(dataloader):
    # compute prediction error
    pred = model(x)
    loss = loss_fn(pred,y)

    # backpropagation
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if batch%100 == 0:
      loss, current = loss.item(), (batch+1) * len(x)
      print(f"loss : {loss:>7f} [{current:>5d}/{size:>5d}]")


def test(dataloader, model, loss_fn):
  size = len(dataloader.dataset)
  num_batches = len(dataloader)

  model.eval()
  test_loss, correct = 0,0

  with torch.no_grad():
    for x, y in dataloader:

      pred = model(x)
      test_loss += loss_fn(pred,y).item()
      correct += (pred.argmax(1) == y).type(torch.float).sum().item()

  test_loss /= num_batches
  correct /= size
  print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")


epochs = 5
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(training_dataloader, model, loss_fn, opt)
    test(testing_dataloader, model, loss_fn)
print("Done!")
