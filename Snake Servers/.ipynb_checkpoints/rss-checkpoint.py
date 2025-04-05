{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cc1254ec-74fc-4daa-93fa-73ea5028900b",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sockets.python3.server import Server\n",
    "from ast import literal_eval\n",
    "import random\n",
    "WIDTH = 800\n",
    "HEIGHT = 600\n",
    "SEG_SIZE = 20\n",
    "\n",
    "class MyServer(Server):\n",
    "    def act_on(self, data, addr):\n",
    "        # Do something with data (in bytes) and return a string.\n",
    "        #return data.decode()\n",
    "        #print(data.decode())\n",
    "        #return \"hello from red socket server!\"\n",
    "        \n",
    "        yx1, yy1, yx2, yy2, x1, y1, x2, y2, ax, ay = literal_eval(data.decode())\n",
    "        print(x1,y1,x2,y2, \"yellow:\", yx1, yy1, yx2, yy2, \"apple:\", ax, ay)\n",
    "        \n",
    "        # Fixing collisions with field edges (or obstacles) for sim\n",
    "        # (in real game, snake hitting obstacles dies!)\n",
    "        if max(x1,x2) >= WIDTH - 20:\n",
    "            #print(\"yellow snake, right wall:\", red_head_coords)\n",
    "            return \"Left\"\n",
    "            \n",
    "        if min(x1,x2) <= 20:\n",
    "            #print(\"yellow snake, left wall:\", red_head_coords)\n",
    "            #y_s.change_direction_ai(\"Right\")\n",
    "            return \"Right\"\n",
    "            \n",
    "        if max(y1,y2) >= HEIGHT - 20:\n",
    "            #print(\"yellow snake, top edge:\", red_head_coords)\n",
    "            return \"Up\"\n",
    "            \n",
    "        if min(y1,y2) <= 20:\n",
    "            #print(\"yellow snake, bottom edge:\", red_head_coords)\n",
    "            return \"Down\"\n",
    "            \n",
    "        # occasional random movements\n",
    "        if random.randint(1,10) == 1:\n",
    "            direction = random.randint(1,4)\n",
    "            if direction == 1:\n",
    "                return \"Up\"\n",
    "            elif direction == 2:\n",
    "                return \"Down\"\n",
    "            elif direction == 3:\n",
    "                return \"Right\"\n",
    "            else:\n",
    "                return \"Left\"\n",
    "\n",
    "        return \"Straight\"\n",
    "\n",
    "server = MyServer(listening_address=('localhost', 5002))\n",
    "server.listen()\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
