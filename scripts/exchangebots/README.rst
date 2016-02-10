****************************************
Decentralized Trading Bot Infrastructure
****************************************

Running
=======

Every configuration has to take place in the ``config.py`` file. There
you can define which markets to serve, the bots to use, and the settings
for each bot.

The bot can be run in single shot only at this time, hence you let the
bot place orders with

::

   $ python3 main.py


After that, you can watch your orders ans have them replaced with 

::

   $ python3 run_cont.py

TODO
====

* [General] Add more strategies
* [General] Monitor and adjust collateral
* [General] Borrow and sell on high premiums
* [Maker] Do not cancel orders if not required

IMPORTANT NOTE
==============

::

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
