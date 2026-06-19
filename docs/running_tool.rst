Running the Tool
=================

To run the tool, ensure that the required Docker volumes are set up. You can do this by using the following command on compute:

.. code-block:: bash

   docker pull veda504/finding_eml:v1.1

.. code-block:: bash

   docker run -it -v "/home/files_dir_path:/mnt" veda504/finding_eml:v1.1 /bin/bash

This command starts a container using the image ``veda504/finding_eml:v1.1`` and mounts the local directory of files into the container at ``/mnt``. It is suggested to use mentioned Docker for running the tool for better results. 

.. raw:: html

    <details>
    <summary>Click to view library versions used in Docker</summary>

.. literalinclude:: _static/requirements.txt
   :language: text

.. raw:: html

    </details>


Once you have set up this environment, you can run the tool either interactively or directly in batch mode. 

To run Finding eML locally, you can choose one of two methods:

*1. Direct Execution:* Execute the script directly for automated processing.

*2. Interactive Execution:* Run the Python shell for real-time interaction.

