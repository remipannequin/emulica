What is Emulica, and  why use it ?
==================================


Emulica is a simulation software that focus on
    * control of manufacturing systems
    * observation of manufacturing systems

Traditionally, simulation has been used to evaluate production systems, 
but didn't focus on control and observation issues. Traditional 
simulation-driven experiments focus on the evaluation of the response (lead 
times, resource utilization, min/average/max queue occupation) of a system under
a certain load: for instance, to evaluate the size of an input buffer in front 
of a machine in a shop floor, or the maximum waiting time of customers in a  
call center... The model used are inspired by a queuing-theory formalism: they 
are structured as a set of server and queues, entities arriving into the system
following a distribution law, and visiting servers in a pre-determined sequence.

If this modeling practice is well adapted to dimensionment issues, it is 
not easily usable if it comes to evaluate more precisely manufacturing control 
issues. Indeed, a big issue when modeling complex manufacturing systems is to 
model decisions taken by operators in the shop floor. This is partially caused 
by the fact that queuing-theory simulation component have often an implicit 
behavior. For instance, when an entity arrive in front of a server, its 
treatment begin as soon as the server is free. As a result, practitioners must 
use modeling "tricks" to integrate more complex decisional behavior into the 
model. Because of this, the comparison of several control strategies require 
to redevelop the whole model.

Another point that was not easy to study using traditional software is the
impact of products observation on manufacturing control. New identification 
technologies (one of the most popular being RFID) that are becoming available 
require a tool able to model various observation strategies, in order to compare
them. For instance, to access the ROI of a planned RFID system, or to determine 
the optimal placement of readers.

Finally, Emulica aims at a more realistic modeling of the physical 
constraints of a shop floor. For instance, traditional simulation models 
includes queues of entities able to sort entity based on a criteria. 
Self-sorting queues don't exist in a real shop floor, even if they may be 
handful for simulating flows in a macroscopic point of view. By using more 
realistic models, we will be able to build a virtual -emulated- shop floor, 
that could be seamlessly replaced by the real one, thus reducing the development
effort of the control system.


